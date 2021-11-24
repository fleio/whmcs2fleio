from typing import List
from typing import Optional

from common.logger import get_fleio_logger

LOG = get_fleio_logger('whmcsync')


class FieldToSync:
    record_name = 'Record'

    def __init__(self, fleio_key: str, whmcs_key: str, fleio_max_length: Optional[int] = None):
        self.fleio_key = fleio_key
        self.whmcs_key = whmcs_key
        self.fleio_max_length = fleio_max_length


def sync_fields(fleio_record, whmcs_record, fields_to_sync: List[FieldToSync]):
    for field in fields_to_sync:
        whmcs_value = getattr(whmcs_record, field.whmcs_key)
        if whmcs_value and isinstance(whmcs_value, str) and len(whmcs_value) > field.fleio_max_length:
            LOG.warning(
                'Had to truncate field {} for {} with ID {}'.format(field.whmcs_key, field.record_name, whmcs_record.id)
            )
            whmcs_value = whmcs_value[:field.fleio_max_length]
        setattr(fleio_record, field.fleio_key, whmcs_value)
