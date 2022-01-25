from django.contrib.auth import get_user_model
from django.db import transaction

from .utils import FieldToSync
from .utils import sync_fields
from ..models import Tblusers
from ..models import TblusersClients
from ..utils import WHMCS_LOGGER

AppUser = get_user_model()


class UserField(FieldToSync):
    record_name = 'User'


def sync_users(fail_fast, related_to_clients=None, with_clients=False):
    exception_list = []
    user_list = []

    u2c_qs = TblusersClients.objects.all()
    qs = Tblusers.objects.all()

    user_ids = None
    if related_to_clients and isinstance(related_to_clients, list) and len(related_to_clients):
        u2c_qs = u2c_qs.filter(client_id__in=related_to_clients)
        user_ids = u2c_qs.values_list('auth_user_id')
    elif with_clients:
        user_ids = u2c_qs.values_list('auth_user_id')

    if user_ids:
        qs = qs.filter(id__in=user_ids)

    for whmcs_user in qs:
        created = False
        try:
            with transaction.atomic():
                fleio_user = AppUser.objects.filter(email=whmcs_user.email).first()
                if not fleio_user:
                    created = True
                    fleio_user = AppUser()

                user_fields_to_sync = []
                if created:
                    # don't change these fields if we only update the user
                    user_fields_to_sync.append(UserField(fleio_key='email', whmcs_key='email', fleio_max_length=254))
                    user_fields_to_sync.append(UserField(fleio_key='username', whmcs_key='email', fleio_max_length=150))
                    user_fields_to_sync.append(UserField(fleio_key='password', whmcs_key='password'))
                user_fields_to_sync.append(
                    UserField(fleio_key='first_name', whmcs_key='first_name', fleio_max_length=150)
                )
                user_fields_to_sync.append(
                    UserField(fleio_key='last_name', whmcs_key='last_name', fleio_max_length=150)
                )
                user_fields_to_sync.append(UserField(fleio_key='last_login', whmcs_key='last_login'))
                # process user fields
                sync_fields(fleio_record=fleio_user, whmcs_record=whmcs_user, fields_to_sync=user_fields_to_sync)
                fleio_user.save()
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            user_list.append(fleio_user)
            if created:
                WHMCS_LOGGER.info(
                    'Created Fleio user {} ({}) from WHMCS ({})'.format(
                        fleio_user.username, fleio_user.id, whmcs_user.id
                    )
                )
            else:
                WHMCS_LOGGER.info(
                    'Updated Fleio user {} ({}) from WHMCS ({})'.format(
                        fleio_user.username, fleio_user.id, whmcs_user.id
                    )
                )
    return user_list, exception_list

