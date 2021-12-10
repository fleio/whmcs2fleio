import markdown
from django.contrib.auth import get_user_model
from django.db import transaction

from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import Tbladmins
from whmcsync.whmcsync.models import Tblticketnotes
from whmcsync.whmcsync.sync.ticket_utils import import_attachment
from whmcsync.whmcsync.sync.utils import match_admin_by_name
from whmcsync.whmcsync.utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import Ticket
except (ImportError, RuntimeError):
    Ticket = None

AppUser = get_user_model()


def parse_note_body(whmcs_note_body, editor):
    return markdown.markdown(whmcs_note_body) if editor and editor == 'markdown' else whmcs_note_body


def match_ticket_note_user(whmcs_ticket_note: Tblticketnotes):
    if whmcs_ticket_note.admin:
        whmcs_admin = match_admin_by_name(admin_name=whmcs_ticket_note.admin)  # type: Tbladmins
        fleio_staff_user = AppUser.objects.filter(email=whmcs_admin.email, is_staff=True).first()
        if not fleio_staff_user:
            raise DBSyncException(
                'Could not match staff user {} for ticket note {}'.format(whmcs_admin.email, whmcs_ticket_note.id)
            )
        return fleio_staff_user


def sync_ticket_notes(fleio_ticket: Ticket, whmcs_ticket_id):
    """
    Imports ticket bites by removing all replies from the ticket up until latest whmcs reply date
    :param fleio_ticket: the ticket from Fleio
    :param whmcs_ticket_id: the id field from WHMCS ticket (not tid!)
    :return:
    """
    with transaction.atomic():
        latest_whmcs_note = Tblticketnotes.objects.filter(ticketid=whmcs_ticket_id).order_by('date').last()
        if not latest_whmcs_note:
            # actually, nothing to sync
            return
        fleio_ticket.notes.filter(created_at__lte=latest_whmcs_note.date).delete()
        for whmcs_ticket_note in Tblticketnotes.objects.filter(ticketid=whmcs_ticket_id):
            fleio_note = fleio_ticket.notes.create(
                created_at=whmcs_ticket_note.date,
                note_text=parse_note_body(
                    whmcs_note_body=whmcs_ticket_note.message, editor=whmcs_ticket_note.editor
                ),
                created_by=match_ticket_note_user(whmcs_ticket_note=whmcs_ticket_note)
            )

            whmcs_attachments = whmcs_ticket_note.attachments.split('|') if whmcs_ticket_note.attachments else None
            if whmcs_attachments:
                for attachment_name in whmcs_attachments:
                    import_attachment(attachment_name=attachment_name, fleio_note=fleio_note)

        if latest_whmcs_note:
            WHMCS_LOGGER.info(
                'Removed all ticket notes for Fleio ticket {} up until {} and '
                're-synced them from WHMCS'.format(fleio_ticket.id, latest_whmcs_note.date)
            )
