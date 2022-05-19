import logging

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from fleio.core.models import Client
from fleio.core.models import ClientGroup
from fleio.core.models import Currency
from .exceptions import SettingsNotConfigured
from .models import Tblclientgroups
from .exceptions import DBSyncException
from .models import Tblclients
from .models import Tblcurrencies

LOG = logging.getLogger('whmcsync')

User = get_user_model()


def verify_settings(ignore_auth_backend=False):
    """Check that all settings are configured in order to proceed"""
    authentication_backend_found = False
    router_found = False
    # NOTE: Check database first
    if settings.DATABASES.get('whmcs') is None:
        raise SettingsNotConfigured('WHMCS database not present in settings.\n'
                                    'Please create a new database named "whmcs" with the same data as your current '
                                    'whmcs database and add the connection settings '
                                    'under DATABASES in Fleio settings\n'
                                    'Ex: DATABASES = {\n      \'default\': {\'ENGINE\': ... },\n'
                                    '      \'whmcs\': {\'ENGINE\': ...}\n    }\n')

    if type(settings.DATABASE_ROUTERS) in (list, tuple):
        for router in settings.DATABASE_ROUTERS:
            if router.split('.')[-1:][0] == 'WhmcSyncRouter':
                router_found = True

    if type(settings.AUTHENTICATION_BACKENDS) in (list, tuple):
        for auth_backend in settings.AUTHENTICATION_BACKENDS:
            if auth_backend.split('.')[-1:][0] == 'WhmcSyncAuthBackend':
                authentication_backend_found = True

    if not router_found:
        raise SettingsNotConfigured('Fleio setting DATABASE_ROUTERS is missing the WhmcSyncRouter \n'
                                    'Example: DATABASE_ROUTERS = [\'whmcsync.whmcsync.routers.WhmcSyncRouter\']\n')
    if not authentication_backend_found:
        msg = ('The WHMCSYNC authentication backend is not present.\n'
               'Passwords will not be synced and WHMCS users won\'t be able to authenticate with their old password.\n'
               'Add the "whmcsync.whmcsync.auth_backend.WhmcSyncAuthBackend" to the AUTHENTICATION_BACKEND setting.\n\n'
               'Ex: AUTHENTICATION_BACKENDS = (\'django.contrib.auth.backends.ModelBackend\','
               ' \'whmcsync.whmcsync.auth_backend.WhmcSyncAuthBackend\')\n\n'
               'Skip this check by adding --ignore-auth-backend to your command\n')
        if ignore_auth_backend:
            LOG.warning(msg)
        else:
            raise SettingsNotConfigured(msg)


def match_currency(whmcs_client):
    """Return matched currency from fleio or raise exception."""
    try:
        return Currency.objects.get(code=whmcs_client.currency.code)
    except Tblcurrencies.DoesNotExist:
        raise DBSyncException(
            'Cannot match currency for WHMCS client {}'.format(whmcs_client.id)
        )
    except Currency.DoesNotExist:
        raise DBSyncException(
            'Cannot match currency {} for WHMCS client {}'.format(whmcs_client.currency.code, whmcs_client.id)
        )


def sync_client_credit(fleio_client: Client, amount, currency_code):
    client_credit, created = fleio_client.credits.get_or_create(currency__code=currency_code,
                                                                defaults={'amount': amount})
    if not created:
        client_credit.amount = amount
        client_credit.save()
    return client_credit


def add_client_groups(fleio_client: Client, whmcs_client: Tblclients):
    whmcs_group_id = whmcs_client.groupid
    if whmcs_group_id:
        try:
            whmcs_group = Tblclientgroups.objects.get(pk=whmcs_group_id)
        except Tblclientgroups.DoesNotExist as e:
            LOG.warning('Unable to sync WHMCS group: {}'.format(whmcs_group_id))
            return
        try:
            fleio_client.groups.get(name=whmcs_group.groupname)
        except ObjectDoesNotExist:
            try:
                fleio_group = ClientGroup.objects.get(name=whmcs_group.groupname)
            except ClientGroup.DoesNotExist:
                LOG.warning(
                    'Unable to sync WHMCS group {} for Fleio client {}. '
                    'Group is missing in Fleio.'.format(whmcs_group.groupname, fleio_client.id)
                )
            else:
                fleio_client.groups.add(fleio_group)
