import markdown
from django.contrib.auth import get_user_model
from django.db import transaction

from fleio.billing.models import Service
from fleio.core.models import Client
from .ticket_notes import sync_ticket_notes
from .ticket_replies import sync_ticket_replies
from .ticket_utils import import_attachment
from .utils import FieldToSync
from .utils import match_admin_by_name
from .utils import sync_fields
from ..exceptions import DBSyncException
from ..models import SyncedAccount
from ..models import Tblclients
from ..models import Tblhosting
from ..models import Tblticketdepartments
from ..models import Tblticketmaillog
from ..models import Tbltickets
from ..models import Tblusers
from ..models.tbladmins import Tbladmins
from ..utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import Department
    from plugins.tickets.models import Ticket
    from plugins.tickets.models.ticket import TicketPriority
    from plugins.tickets.models.ticket import TicketStatus
    from plugins.tickets.models import EmailMessage
except (ImportError, RuntimeError):
    Department = None
    Ticket = None
    TicketPriority = None
    TicketStatus = None
    EmailMessage = None

AppUser = get_user_model()


class TicketField(FieldToSync):
    record_name = 'Ticket'


TICKET_FIELDS_TO_SYNC = [
    TicketField(fleio_key='title', whmcs_key='title', fleio_max_length=1024),
    TicketField(fleio_key='last_reply_at', whmcs_key='lastreply'),
    TicketField(fleio_key='created_at', whmcs_key='date'),
    TicketField(fleio_key='cc_recipients', whmcs_key='cc', fleio_max_length=1024)
]


def parse_ticket_body(whmcs_ticket_body, editor):
    return markdown.markdown(whmcs_ticket_body) if editor and editor == 'markdown' else whmcs_ticket_body


def match_ticket_service(whmcs_ticket_service, fleio_client):
    if whmcs_ticket_service and fleio_client:
        service_txt_split = whmcs_ticket_service.split('S')
        if len(service_txt_split) > 1 and len(service_txt_split[0]) == 0:
            whmcs_service_id = Tblhosting.objects.filter(id=service_txt_split[1]).first()
            if whmcs_service_id:
                return Service.objects.filter(client=fleio_client, external_billing_id=whmcs_service_id).first()
    return None


def match_ticket_merge(whmcs_ticket: Tbltickets):
    if not whmcs_ticket.merged_ticket_id:
        return None
    merged_into = Tbltickets.objects.get(id=whmcs_ticket.merged_ticket_id)
    fleio_ticket = Ticket.objects.filter(id=merged_into.tid).first()
    if not fleio_ticket:
        raise DBSyncException(
            'Could not match merged ticket {} for ticket {}'.format(whmcs_ticket.merged_ticket_id, whmcs_ticket.id)
        )
    return fleio_ticket


def match_ticket_status(whmcs_ticket: Tbltickets):
    if whmcs_ticket.status == 'Open':
        return TicketStatus.open
    elif whmcs_ticket.status == 'Answered':
        return TicketStatus.answered
    elif whmcs_ticket.status == 'Customer-Reply':
        return TicketStatus.customer_reply
    elif whmcs_ticket.status == 'On Hold':
        return TicketStatus.on_hold
    elif whmcs_ticket.status == 'In Progress':
        return TicketStatus.in_progress
    elif whmcs_ticket.status == 'Closed':
        if whmcs_ticket.merged_ticket_id:
            return TicketStatus.merged
        else:
            return TicketStatus.done
    else:
        raise DBSyncException('Cannot match ticket status {}'.format(whmcs_ticket.status))


def match_ticket_priority(whmcs_ticket_urgency):
    if whmcs_ticket_urgency == 'Medium':
        return TicketPriority.medium
    elif whmcs_ticket_urgency == 'High':
        return TicketPriority.high
    elif whmcs_ticket_urgency == 'Low':
        return TicketPriority.low
    else:
        raise DBSyncException('Cannot match ticket priority {}'.format(whmcs_ticket_urgency))


def match_ticket_department(whmcs_ticket: Tbltickets):
    if not whmcs_ticket.did:
        raise DBSyncException(
            'Cannot sync whmcs ticket {} without department while Fleio requires one'.format(whmcs_ticket.id)
        )
    whmcs_department = Tblticketdepartments.objects.get(id=whmcs_ticket.did)
    fleio_department = Department.objects.filter(email=whmcs_department.email).first()
    if not fleio_department:
        raise DBSyncException(
            'Could not match department {} for ticket {}'.format(whmcs_department.email, whmcs_ticket.id)
        )
    return fleio_department


def match_ticket_client(whmcs_ticket: Tbltickets):
    if not whmcs_ticket.userid:
        return None
    whmcs_client = Tblclients.objects.get(id=whmcs_ticket.userid)
    synced_account = SyncedAccount.objects.filter(
        whmcs_id=whmcs_ticket.userid,
        whmcs_uuid=whmcs_client.uuid
    ).first()
    fleio_client = synced_account.client if synced_account else Client.objects.filter(
        external_billing_id=whmcs_client.uuid
    ).first()
    if not fleio_client:
        raise DBSyncException(
            'Could not match client {} for ticket {}'.format(whmcs_ticket.userid, whmcs_ticket.id)
        )
    return fleio_client


def match_ticket_user(whmcs_ticket: Tbltickets):
    if whmcs_ticket.requestor_id:
        whmcs_user = Tblusers.objects.get(id=whmcs_ticket.requestor_id)
        fleio_user = AppUser.objects.filter(email=whmcs_user.email).first()
        if not fleio_user:
            raise DBSyncException(
                'Could not match user {} for ticket {}'.format(whmcs_ticket.requestor_id, whmcs_ticket.id)
            )
        return fleio_user
    elif whmcs_ticket.admin:
        whmcs_admin = match_admin_by_name(admin_name=whmcs_ticket.admin)  # type: Tbladmins
        fleio_staff_user = AppUser.objects.filter(email=whmcs_admin.email, is_staff=True).first()
        if not fleio_staff_user:
            raise DBSyncException(
                'Could not match staff user {} for ticket {}'.format(whmcs_admin.email, whmcs_ticket.id)
            )
        return fleio_staff_user


def match_ticket_assigned_to(whmcs_ticket: Tbltickets):
    if whmcs_ticket.flag:
        whmcs_admin = Tbladmins.objects.get(id=whmcs_ticket.flag)
        fleio_staff_user = AppUser.objects.filter(email=whmcs_admin.email, is_staff=True).first()
        if not fleio_staff_user:
            raise DBSyncException(
                'Could not match assigned staff user {} for ticket {}'.format(whmcs_admin.email, whmcs_ticket.id)
            )
        return fleio_staff_user


def sync_tickets(fail_fast, whmcs_ids=None):
    exception_list = []
    tickets_list = []
    qs = Tbltickets.objects.all()
    if whmcs_ids:
        qs = qs.filter(id__in=whmcs_ids)
    for whmcs_ticket in qs.order_by('id'):
        try:
            with transaction.atomic():
                created = False
                fleio_ticket = Ticket.objects.filter(id=whmcs_ticket.tid).first()
                if not fleio_ticket:
                    created = True
                    fleio_ticket = Ticket(id=whmcs_ticket.tid)

                # process ticket fields
                sync_fields(fleio_record=fleio_ticket, whmcs_record=whmcs_ticket, fields_to_sync=TICKET_FIELDS_TO_SYNC)

                ticket_client = match_ticket_client(whmcs_ticket=whmcs_ticket)
                fleio_ticket.description = parse_ticket_body(
                    whmcs_ticket_body=whmcs_ticket.message, editor=whmcs_ticket.editor
                )
                ticket_user = match_ticket_user(whmcs_ticket=whmcs_ticket)
                fleio_ticket.created_by = ticket_user
                fleio_ticket.assigned_to = match_ticket_assigned_to(whmcs_ticket=whmcs_ticket)
                fleio_ticket.client = ticket_client
                fleio_ticket.department = match_ticket_department(whmcs_ticket=whmcs_ticket)
                fleio_ticket.priority = match_ticket_priority(whmcs_ticket_urgency=whmcs_ticket.urgency)
                fleio_ticket.status = match_ticket_status(whmcs_ticket=whmcs_ticket)
                fleio_ticket.service = match_ticket_service(
                    whmcs_ticket_service=whmcs_ticket.service,
                    fleio_client=ticket_client,
                )
                fleio_ticket.merged_into = match_ticket_merge(whmcs_ticket=whmcs_ticket)
                fleio_ticket.save(fleio_external=True)

                if not ticket_user and whmcs_ticket.email:
                    # try to find related mail log, if not found, use data from ticket
                    whmcs_mail_log = Tblticketmaillog.objects.filter(
                        date=whmcs_ticket.date,
                        email=whmcs_ticket.email,
                    ).first()
                    if whmcs_mail_log:
                        email_message = EmailMessage.objects.get_or_create(
                            sender_address=whmcs_mail_log.email,
                            to=whmcs_mail_log.to,
                            cc=whmcs_mail_log.cc,
                            subject=whmcs_mail_log.subject,
                            body=whmcs_mail_log.message,
                            message_id=None,
                        )
                    else:
                        # mail log not found, create email message with what we have
                        email_message = EmailMessage.objects.get_or_create(
                            sender_address=whmcs_ticket.email,
                            to=fleio_ticket.department.email,
                            cc=fleio_ticket.cc,
                            subject=fleio_ticket.title,
                            body=fleio_ticket.description,
                            message_id=None,
                        )
                    fleio_ticket.email_message = email_message
                    fleio_ticket.save(update_fields=['email_message'])

                if created:
                    whmcs_attachments = whmcs_ticket.attachment.split('|') if whmcs_ticket.attachment else None
                    if whmcs_attachments:
                        for attachment_name in whmcs_attachments:
                            import_attachment(attachment_name=attachment_name, fleio_ticket=fleio_ticket)

                WHMCS_LOGGER.debug('Ticket {} synced. Starting to sync replies & notes.'.format(fleio_ticket.id))
                sync_ticket_replies(fleio_ticket=fleio_ticket, whmcs_ticket_id=whmcs_ticket.id)
                sync_ticket_notes(fleio_ticket=fleio_ticket, whmcs_ticket_id=whmcs_ticket.id)

        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            tickets_list.append(fleio_ticket)
            if created:
                WHMCS_LOGGER.info('Created ticket {}'.format(fleio_ticket.id))
            else:
                WHMCS_LOGGER.info('Updated ticket {}'.format(fleio_ticket.id))
    return tickets_list, exception_list
