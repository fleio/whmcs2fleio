from typing import List
from typing import Optional

from common.logger import get_fleio_logger
from fleio.conf.utils import fernet_encrypt
from whmcsync.whmcsync.exceptions import DBSyncException

LOG = get_fleio_logger('whmcsync')


class FieldToSync:
    record_name = 'Record'

    def __init__(self, fleio_key: str, whmcs_key: str, fleio_max_length: Optional[int] = None, encrypt: bool = False,
                 default=None):
        self.fleio_key = fleio_key
        self.whmcs_key = whmcs_key
        self.fleio_max_length = fleio_max_length
        self.encrypt = encrypt
        self.default = default


def sync_fields(fleio_record, whmcs_record, fields_to_sync: List[FieldToSync]):
    for field in fields_to_sync:
        whmcs_value = getattr(whmcs_record, field.whmcs_key)
        if whmcs_value and isinstance(whmcs_value, str) and len(whmcs_value) > field.fleio_max_length:
            if field.encrypt:
                raise DBSyncException(
                    'WHMCS {} value cannot be saved because it already overflows Fleio related field ({}) max_length '
                    'and also has to be encrypted'.format(field.whmcs_key, field.fleio_key)
                )
            LOG.warning(
                'Had to truncate field {} for {} with ID {}'.format(field.whmcs_key, field.record_name, whmcs_record.id)
            )
            whmcs_value = whmcs_value[:field.fleio_max_length]
        if field.encrypt and whmcs_value and isinstance(whmcs_value, str):
            whmcs_value = fernet_encrypt(whmcs_value)
        if whmcs_value is None and field.default is not None:
            whmcs_value = field.default
        setattr(fleio_record, field.fleio_key, whmcs_value)
