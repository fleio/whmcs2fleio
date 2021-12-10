from datetime import datetime
from typing import List
from typing import Optional

from django.utils import timezone

from fleio.conf.utils import fernet_encrypt
from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import Tbladmins
from whmcsync.whmcsync.utils import WHMCS_LOGGER


class FieldToSync:
    record_name = 'Record'

    def __init__(self, fleio_key: str, whmcs_key: str, fleio_max_length: Optional[int] = None, encrypt: bool = False,
                 default=None):
        self.fleio_key = fleio_key
        self.whmcs_key = whmcs_key
        self.fleio_max_length = fleio_max_length
        self.encrypt = encrypt
        self.default = default

    def __str__(self):
        return '{} - {}'.format(self.record_name, self.fleio_key)


def sync_fields(fleio_record, whmcs_record, fields_to_sync: List[FieldToSync]):
    for field in fields_to_sync:
        try:
            whmcs_value = getattr(whmcs_record, field.whmcs_key)
            if (field.fleio_max_length and whmcs_value and isinstance(whmcs_value, str) and
                    len(whmcs_value) > field.fleio_max_length):
                if field.encrypt:
                    raise DBSyncException(
                        'WHMCS {} value cannot be saved because it already overflows Fleio related field ({}) '
                        'max_length and also has to be encrypted'.format(field.whmcs_key, field.fleio_key)
                    )
                WHMCS_LOGGER.warning(
                    'Had to truncate field {} for {} with ID {}'.format(
                        field.whmcs_key, field.record_name, whmcs_record.id
                    )
                )
                whmcs_value = whmcs_value[:field.fleio_max_length]
            if field.encrypt and whmcs_value and isinstance(whmcs_value, str):
                whmcs_value = fernet_encrypt(whmcs_value)
            if whmcs_value is None and field.default is not None:
                whmcs_value = field.default
            setattr(fleio_record, field.fleio_key, whmcs_value)
        except TypeError as e:
            WHMCS_LOGGER.error('Error while trying to set field {}: {}'.format(field.fleio_key, e))
            raise


def set_tz(date_time, tz=timezone.utc):
    return timezone.make_aware(date_time, timezone=tz)


def date_to_datetime(date):
    if not date:
        return None
    dt = datetime.combine(date, datetime.min.time())
    return set_tz(dt, tz=timezone.utc)


def match_admin_by_name(admin_name: str):
    if not admin_name:
        return None
    possible_related_admins = Tbladmins.objects.all()
    for possible_related_admin in possible_related_admins:
        if '{} {}'.format(possible_related_admin.firstname, possible_related_admin.lastname) == admin_name:
            return possible_related_admin
    return None
