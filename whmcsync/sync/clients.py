import decimal
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from fleio.core.models import Client
from fleio.core.models import ClientStatus
from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblclients
from whmcsync.whmcsync.operations import add_client_groups
from whmcsync.whmcsync.operations import match_currency
from whmcsync.whmcsync.operations import sync_client_credit
from whmcsync.whmcsync.sync.client_contacts import sync_client_contacts
from whmcsync.whmcsync.sync.utils import FieldToSync
from whmcsync.whmcsync.sync.utils import sync_fields
from whmcsync.whmcsync.utils import WHMCS_LOGGER


class ClientField(FieldToSync):
    record_name = 'Client'


CLIENT_FIELDS_TO_SYNC = [
    ClientField(fleio_key='first_name', whmcs_key='firstname', fleio_max_length=127),
    ClientField(fleio_key='last_name', whmcs_key='lastname', fleio_max_length=127),
    ClientField(fleio_key='company', whmcs_key='companyname', fleio_max_length=127),
    ClientField(fleio_key='address1', whmcs_key='address1', fleio_max_length=255),
    ClientField(fleio_key='address2', whmcs_key='address2', fleio_max_length=255),
    ClientField(fleio_key='city', whmcs_key='city', fleio_max_length=127),
    ClientField(fleio_key='country', whmcs_key='country', fleio_max_length=2),
    ClientField(fleio_key='state', whmcs_key='state', fleio_max_length=127),
    ClientField(fleio_key='zip_code', whmcs_key='postcode', fleio_max_length=10),
    ClientField(fleio_key='phone', whmcs_key='phonenumber', fleio_max_length=64),
    ClientField(fleio_key='email', whmcs_key='email', fleio_max_length=127),
    ClientField(fleio_key='vat_id', whmcs_key='tax_id', fleio_max_length=32),
    ClientField(fleio_key='tax_exempt', whmcs_key='taxexempt'),
]


def sync_client(id, whmcs_client=None):
    """Synchronizes WHMCS clients."""
    add_partially_synced_account = False
    if whmcs_client is None:
        try:
            whmcs_client = Tblclients.objects.get(id=id)
        except (Tblclients.DoesNotExist, ValueError):
            raise DBSyncException('WHMCS client ID %s is not valid.' % id)

    # check if client already exists from a previous import
    synced_account = SyncedAccount.objects.filter(
        whmcs_id=whmcs_client.pk,
        whmcs_uuid=whmcs_client.uuid,
        subaccount=False
    ).first()
    if synced_account:
        client = synced_account.client
    else:
        add_partially_synced_account = True  # we shall add a synced account without user for later use
        # check if client already exists because of using fleio-whmcs module
        # and not because of using a previous import
        client = Client.objects.filter(external_billing_id=whmcs_client.uuid).first()

    if not client:
        client = Client()

    # process client fields
    sync_fields(fleio_record=client, whmcs_record=whmcs_client, fields_to_sync=CLIENT_FIELDS_TO_SYNC)

    whmcs_status_to_fleio = whmcs_client.status.lower()
    if whmcs_status_to_fleio not in ClientStatus.name_map.keys():
        WHMCS_LOGGER.warning(
            'WHMCS client {} status not compatible with Fleio statuses. Fallback on inactive status.'.format(id)
        )
        whmcs_status_to_fleio = ClientStatus.inactive
    client.status = whmcs_status_to_fleio

    client.currency = match_currency(whmcs_client)
    client.uptodate_credit = decimal.Decimal('0.00')

    if whmcs_client.created_at:
        client.date_created = whmcs_client.created_at
    elif whmcs_client.datecreated:
        whmcs_date_created = datetime.combine(whmcs_client.datecreated, datetime.min.time())
        whmcs_date_created = timezone.make_aware(whmcs_date_created, timezone=timezone.utc)
        client.date_created = whmcs_date_created

    with transaction.atomic():
        client.save()
        sync_client_credit(fleio_client=client, amount=whmcs_client.credit, currency_code=whmcs_client.currency.code)

        if add_partially_synced_account:
            # add new synced account without user (will be populated later)
            SyncedAccount.objects.create(
                whmcs_id=whmcs_client.id,
                whmcs_uuid=whmcs_client.uuid,
                client=client,
                user=None,
                subaccount=False
            )
        add_client_groups(fleio_client=client, whmcs_client=whmcs_client)
        sync_client_contacts(fleio_client=client, whmcs_client=whmcs_client)
    return whmcs_client.id


def sync_clients(fail_fast, whmcs_ids=None, active_only=False):
    """Synchronizes all WHMCS clients and users."""
    exception_list = []
    client_list = []
    qs = Tblclients.objects.all()
    if whmcs_ids and isinstance(whmcs_ids, list) and len(whmcs_ids):
        qs = qs.filter(id__in=whmcs_ids)
    if active_only:
        qs = qs.filter(status='Active')
    for client in qs:
        try:
            synced_id = sync_client(id=client.id, whmcs_client=client)
            client_list.append('{} {} - {} (ID: {})'.format(client.firstname,
                                                            client.lastname,
                                                            client.companyname,
                                                            synced_id))
        except Exception as ex:
            WHMCS_LOGGER.exception(ex)
            if fail_fast:
                exception_list.append(ex)
                break
            else:
                exception_list.append(ex)
    return client_list, exception_list
