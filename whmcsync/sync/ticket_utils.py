import os
import mimetypes

from whmcsync.whmcsync.utils import WHMCS_LOGGER

try:
    from plugins.tickets.common.attachments_storage import AttachmentsStorage
    from plugins.tickets.models import Attachment
except (ImportError, RuntimeError):
    AttachmentsStorage = None
    Attachment = None

WHMCS_ATTACHMENTS_DIR = '{}/attachments'.format(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def import_attachment(attachment_name, fleio_ticket=None, fleio_reply=None, fleio_note=None):
    attachment_storage = AttachmentsStorage.get_attachments_storage()
    whmcs_id, filename = attachment_name.split('_', 1)
    disk_file_name = attachment_storage.create_disk_file_name(filename)
    attachment_path = '{}/{}'.format(WHMCS_ATTACHMENTS_DIR, attachment_name)
    try:
        with open(attachment_path, 'rb') as attachment_file:
            attachment_storage.save_attachment(disk_file_name=disk_file_name, attachment_data=attachment_file.read())
            content_type = mimetypes.guess_type(attachment_path)[0]
            Attachment.objects.create(
                content_type=content_type,
                file_name=filename,
                disk_file=disk_file_name,
                ticket=fleio_ticket,
                ticket_update=fleio_reply,
                ticket_note=fleio_note,
            )
    except FileNotFoundError:
        WHMCS_LOGGER.error(
            'Attachment {} was not found thus cannot import related ticket/reply/note. '
            'Did you add WHMCS attachments dir content to {}?'.format(attachment_name, WHMCS_ATTACHMENTS_DIR)
        )
        raise
