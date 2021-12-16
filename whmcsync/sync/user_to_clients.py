from django.contrib.auth import get_user_model
from django.db import transaction

from fleio.core.models import Client
from fleio.core.models import UserToClient
from ..models import SyncedAccount
from ..models import Tblclients
from ..models import Tblusers
from ..models import TblusersClients
from ..utils import WHMCS_LOGGER

AppUser = get_user_model()


def get_partially_synced_account(whmcs_client: Tblclients, fleio_client: Client) -> SyncedAccount:
    synced_account, created = SyncedAccount.objects.get_or_create(
        whmcs_id=whmcs_client.pk,
        whmcs_uuid=whmcs_client.uuid,
        client=fleio_client,
        user=None,
        subaccount=False
    )
    return synced_account


def get_related_fleio_client(whmcs_client: Tblclients):
    """Gets related Fleio client that did not have u2c client synced yet"""
    synced_account = SyncedAccount.objects.filter(
        whmcs_id=whmcs_client.pk,
        whmcs_uuid=whmcs_client.uuid,
        subaccount=False
    ).first()
    return Client.objects.filter(
        external_billing_id=whmcs_client.uuid
    ).first() if not synced_account else synced_account.client


def get_related_fleio_user(whmcs_user_id):
    whmcs_user = Tblusers.objects.filter(id=whmcs_user_id).first()
    return AppUser.objects.filter(email=whmcs_user.email).first()


def sync_user_to_clients(fail_fast, related_to_clients=None):
    exception_list = []
    u2c_list = []
    qs = TblusersClients.objects.all()
    if related_to_clients and isinstance(related_to_clients, list) and len(related_to_clients):
        qs = qs.filter(client_id__in=related_to_clients)

    for whmcs_u2c in qs:
        try:
            whmcs_client = Tblclients.objects.filter(id=whmcs_u2c.client_id).first()
            fleio_client = get_related_fleio_client(whmcs_client=whmcs_client)
            if not fleio_client:
                WHMCS_LOGGER.warning(
                    'Cannot sync UserToClient (whmcs id: {}) as related client ({}) is not synced in Fleio.'.format(
                        whmcs_u2c.id, whmcs_u2c.client_id
                    )
                )
                continue
            fleio_user = get_related_fleio_user(whmcs_user_id=whmcs_u2c.auth_user_id)
            if not fleio_user:
                WHMCS_LOGGER.warning(
                    'Cannot sync UserToClient (whmcs id: {}) as related user ({}) is not synced in Fleio.'.format(
                        whmcs_u2c.id, whmcs_u2c.auth_user_id
                    )
                )
                continue
            with transaction.atomic():
                # owner role should be automatically added
                fleio_u2c, created = UserToClient.objects.get_or_create(
                    user=fleio_user,
                    client=fleio_client
                )

                partially_synced_account = get_partially_synced_account(
                    whmcs_client=whmcs_client,
                    fleio_client=fleio_client,
                )  # type: SyncedAccount
                if partially_synced_account:
                    partially_synced_account.user = fleio_user
                    partially_synced_account.save(update_fields=['user'])
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            u2c_list.append(fleio_u2c)
            if created:
                WHMCS_LOGGER.info('Imported user to client relation {}'.format(fleio_u2c))
    return u2c_list, exception_list

