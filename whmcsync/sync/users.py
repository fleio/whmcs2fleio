from django.contrib.auth import get_user_model

from common.logger import get_fleio_logger
from .utils import FieldToSync
from .utils import sync_fields
from ..models import Tblusers
from ..models import TblusersClients

AppUser = get_user_model()
LOG = get_fleio_logger('whmcsync')


class UserField(FieldToSync):
    record_name = 'User'


def sync_users(fail_fast, related_to_clients=None):
    exception_list = []
    user_list = []
    user_ids = None
    if related_to_clients and isinstance(related_to_clients, list) and len(related_to_clients):
        user_ids = TblusersClients.objects.filter(client_id__in=related_to_clients).values_list('auth_user_id')
    users_qs = Tblusers.objects.filter(id__in=user_ids) if (user_ids and len(user_ids)) else Tblusers.objects.all()

    for whmcs_user in users_qs:
        created = False
        try:
            fleio_user = AppUser.objects.filter(email=whmcs_user.email, username=whmcs_user.email).first()
            if not fleio_user:
                created = True
                fleio_user = AppUser()

            user_fields_to_sync = []
            if created:
                # don't change these fields if we only update the user
                user_fields_to_sync.append(UserField(fleio_key='email', whmcs_key='email', fleio_max_length=254))
                user_fields_to_sync.append(UserField(fleio_key='username', whmcs_key='email', fleio_max_length=150))
                user_fields_to_sync.append(UserField(fleio_key='password', whmcs_key='password'))
            user_fields_to_sync.append(UserField(fleio_key='first_name', whmcs_key='first_name', fleio_max_length=150))
            user_fields_to_sync.append(UserField(fleio_key='last_name', whmcs_key='last_name', fleio_max_length=150))
            user_fields_to_sync.append(UserField(fleio_key='last_login', whmcs_key='last_login'))
            # process user fields
            sync_fields(fleio_record=fleio_user, whmcs_record=whmcs_user, fields_to_sync=user_fields_to_sync)
            fleio_user.save()
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            user_list.append(fleio_user)
            if created:
                LOG.info(
                    'Created Fleio user {} ({}) from WHMCS ({})'.format(
                        fleio_user.username, fleio_user.id, whmcs_user.id
                    )
                )
            else:
                LOG.info(
                    'Updated Fleio user {} ({}) from WHMCS ({})'.format(
                        fleio_user.username, fleio_user.id, whmcs_user.id
                    )
                )
    return user_list, exception_list

