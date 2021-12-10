import markdown
from django.contrib.auth import get_user_model
from django.db import transaction

from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import Tbladmins
from whmcsync.whmcsync.models import Tblticketmaillog
from whmcsync.whmcsync.models import Tblticketreplies
from whmcsync.whmcsync.models import Tblusers
from whmcsync.whmcsync.sync.ticket_utils import import_attachment
from whmcsync.whmcsync.sync.utils import match_admin_by_name
from whmcsync.whmcsync.utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import Ticket
    from plugins.tickets.models import EmailMessage
    from plugins.tickets.models import TicketUpdate
except (ImportError, RuntimeError):
    Ticket = None
    EmailMessage = None
    TicketUpdate = None

AppUser = get_user_model()


def parse_reply_body(whmcs_reply_body, editor):
    return markdown.markdown(whmcs_reply_body) if editor and editor == 'markdown' else whmcs_reply_body


def match_ticket_reply_user(whmcs_ticket_reply: Tblticketreplies):
    if whmcs_ticket_reply.requestor_id:
        # in this case, client & user ids do not match, we use this with priority
        whmcs_user = Tblusers.objects.get(id=whmcs_ticket_reply.requestor_id)
        fleio_user = AppUser.objects.filter(email=whmcs_user.email).first()
        if not fleio_user:
            raise DBSyncException(
                'Could not match user {} for ticket reply {}'.format(
                    whmcs_ticket_reply.requestor_id, whmcs_ticket_reply.id
                )
            )
        return fleio_user
    elif whmcs_ticket_reply.userid:
        # in this case, id is the same for both client & user, fallback if requestor_id is not defined
        whmcs_user = Tblusers.objects.get(id=whmcs_ticket_reply.userid)
        fleio_user = AppUser.objects.filter(email=whmcs_user.email).first()
        if not fleio_user:
            raise DBSyncException(
                'Could not match user {} for ticket reply {}'.format(
                    whmcs_ticket_reply.userid, whmcs_ticket_reply.id
                )
            )
        return fleio_user
    elif whmcs_ticket_reply.admin:
        whmcs_admin = match_admin_by_name(admin_name=whmcs_ticket_reply.admin)  # type: Tbladmins
        fleio_staff_user = AppUser.objects.filter(email=whmcs_admin.email, is_staff=True).first()
        if not fleio_staff_user:
            raise DBSyncException(
                'Could not match staff user {} for ticket reply {}'.format(whmcs_admin.email, whmcs_ticket_reply.id)
            )
        return fleio_staff_user


def sync_ticket_replies(fleio_ticket: Ticket, whmcs_ticket_id):
    """
    Imports ticket replies by removing all replies from the ticket up until latest whmcs reply date
    :param fleio_ticket: the ticket from Fleio
    :param whmcs_ticket_id: the id field from WHMCS ticket (not tid!)
    :return:
    """
    with transaction.atomic():
        latest_whmcs_reply = Tblticketreplies.objects.filter(tid=whmcs_ticket_id).order_by('date').last()
        if not latest_whmcs_reply:
            # actually, nothing to sync
            return
        fleio_ticket.updates.filter(created_at__lte=latest_whmcs_reply.date).delete()
        for whmcs_ticket_reply in Tblticketreplies.objects.filter(tid=whmcs_ticket_id):
            reply_user = match_ticket_reply_user(whmcs_ticket_reply=whmcs_ticket_reply)
            fleio_reply = fleio_ticket.updates.create(
                created_at=whmcs_ticket_reply.date,
                reply_text=parse_reply_body(
                    whmcs_reply_body=whmcs_ticket_reply.message, editor=whmcs_ticket_reply.editor
                ),
                created_by=reply_user
            )  # type: TicketUpdate

            if not reply_user and whmcs_ticket_reply.email:
                # try to find related mail log, if not found, use data from ticket
                whmcs_mail_log = Tblticketmaillog.objects.filter(
                    date=whmcs_ticket_reply.date,
                    email=whmcs_ticket_reply.email,
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
                        sender_address=whmcs_ticket_reply.email,
                        to=fleio_ticket.department.email,
                        cc=None,
                        subject=None,
                        body=fleio_reply.reply_text,
                        message_id=None,
                    )
                fleio_reply.email_message = email_message
                fleio_reply.save(update_fields=['email_message'])

            whmcs_attachments = whmcs_ticket_reply.attachment.split('|') if whmcs_ticket_reply.attachment else None
            if whmcs_attachments:
                for attachment_name in whmcs_attachments:
                    import_attachment(attachment_name=attachment_name, fleio_reply=fleio_reply)

        if latest_whmcs_reply:
            WHMCS_LOGGER.info(
                'Removed all ticket replies for Fleio ticket {} up until {} and '
                're-synced them from WHMCS'.format(fleio_ticket.id, latest_whmcs_reply.date)
            )
