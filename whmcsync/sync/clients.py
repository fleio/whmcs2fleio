import logging
import decimal

from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblclients

from fleio.core.models import Client
from fleio.core.models import UserToClient
from whmcsync.whmcsync.operations import add_client_groups
from whmcsync.whmcsync.operations import match_currency
from whmcsync.whmcsync.operations import sync_client_credit
from whmcsync.whmcsync.sync.client_contacts import sync_client_contacts

LOG = logging.getLogger('whmcsync')
User = get_user_model()


def sync_client(id, whmcs_client=None):
    """Synchronizes WHMCS clients and users."""
    create = False
    if whmcs_client is None:
        try:
            whmcs_client = Tblclients.objects.get(id=id)
        except (Tblclients.DoesNotExist, ValueError):
            raise DBSyncException('WHMCS client ID %s is not valid.' % id)

    try:
        synced_client = SyncedAccount.objects.get(whmcs_id=whmcs_client.pk,
                                                  whmcs_uuid=whmcs_client.uuid,
                                                  subaccount=False)
        client = synced_client.client
        user = synced_client.user
    except SyncedAccount.DoesNotExist:
        try:
            User.objects.get(username=whmcs_client.email)
            raise DBSyncException('User %s already exists in Fleio database.' % whmcs_client.email)
        except User.DoesNotExist:
            create = True
            user = User()
            client = Client()

    user.username = whmcs_client.email
    user.password = whmcs_client.password
    user.first_name = whmcs_client.firstname[:30]
    user.last_name = whmcs_client.lastname[:150]
    user.email = whmcs_client.email
    user.last_login = whmcs_client.lastlogin
    user.is_active = 'Active' in whmcs_client.status

    client.first_name = whmcs_client.firstname[:127]
    client.last_name = whmcs_client.lastname[:127]
    client.company = whmcs_client.companyname[:127]
    client.address1 = whmcs_client.address1
    client.address2 = whmcs_client.address2
    client.city = whmcs_client.city
    client.country = whmcs_client.country
    client.state = whmcs_client.state
    client.zip_code = whmcs_client.postcode[:10]
    client.phone = whmcs_client.phonenumber
    client.email = whmcs_client.email
    client.created_at = whmcs_client.created_at
    client.tax_exempt = whmcs_client.taxexempt
    client.status = whmcs_client.status.lower()
    client.currency = match_currency(whmcs_client)
    client.uptodate_credit = decimal.Decimal('0.00')

    if whmcs_client.datecreated:
        whmcs_date_created = datetime.combine(whmcs_client.datecreated, datetime.min.time())
        whmcs_date_created = timezone.make_aware(whmcs_date_created, timezone=timezone.utc)
        user.date_joined = whmcs_date_created
        client.date_created = whmcs_date_created
    elif whmcs_client.created_at:
        user.date_joined = whmcs_client.created_at
        client.date_created = whmcs_client.created_at

    with transaction.atomic():
        user.save()
        client.save()
        sync_client_credit(fleio_client=client, amount=whmcs_client.credit, currency_code=whmcs_client.currency.code)

        if create:
            usertoclient = UserToClient()
            usertoclient.user = user
            usertoclient.client = client
            usertoclient.save()
            synced_client = SyncedAccount()
            synced_client.whmcs_id = whmcs_client.id
            synced_client.whmcs_uuid = whmcs_client.uuid
            synced_client.client = client
            synced_client.user = user
            synced_client.save()
        add_client_groups(fleio_client=client, whmcs_client=whmcs_client)
        sync_client_contacts(fleio_client=client, whmcs_client=whmcs_client)
    return whmcs_client.id


def sync_all_clients(fail_fast):
    """Synchronizes all WHMCS clients and users."""
    exception_list = []
    client_list = []
    for client in Tblclients.objects.all():
        try:
            synced_id = sync_client(id=client.id, whmcs_client=client)
            client_list.append('{} {} - {} (ID: {})'.format(client.firstname,
                                                            client.lastname,
                                                            client.companyname,
                                                            synced_id))
        except DBSyncException as ex:
            LOG.exception(ex)
            if fail_fast:
                exception_list.append(ex)
                break
            else:
                exception_list.append(ex)
    return client_list, exception_list
