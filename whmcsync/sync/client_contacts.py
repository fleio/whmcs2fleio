import logging

from django.db import transaction

from fleio.core.models import Client
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblclients
from .utils import FieldToSync
from .utils import sync_fields
from ..models import Tblcontacts

try:
    from plugins.domains.models import Contact
except (ImportError, RuntimeError):
    Contact = None

LOG = logging.getLogger('whmcsync')


class ClientField(FieldToSync):
    record_name = 'Contact'


CONTACT_FIELDS_TO_SYNC = [
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
    ClientField(fleio_key='created_at', whmcs_key='created_at'),
]


def sync_client_contacts(fleio_client: Client, whmcs_client: Tblclients):
    """Place client contacts in client domain contacts and create additional users if contacts have sub accounts"""
    synced_contacts = 0
    for wcontact in Tblcontacts.objects.filter(userid=whmcs_client.id):
        with transaction.atomic():
            synced_account = SyncedAccount.objects.filter(
                whmcs_id=whmcs_client.id, whmcs_uuid=whmcs_client.uuid
            ).first()
            existing_client = synced_account.client if synced_account else Client.objects.filter(
                external_billing_id=whmcs_client.uuid
            ).first()
            if not existing_client:
                LOG.warning(
                    'Skip contact {} for client {}. Client not synced'.format(wcontact.firstname, whmcs_client.id)
                )
                continue

            created = False
            contact = Contact.objects.filter(client=fleio_client, email=wcontact.email).first()
            if not contact:
                created = True
                contact = Contact(
                    client=fleio_client,
                )

            # process contact fields
            sync_fields(fleio_record=contact, whmcs_record=wcontact, fields_to_sync=CONTACT_FIELDS_TO_SYNC)
            contact.save()

            if created:
                LOG.info('Created contact {} for {} ({})'.format(contact.name, contact.client.name, contact.client_id))
            else:
                LOG.info('Updated contact {} for {} ({})'.format(contact.name, contact.client.name, contact.client_id))

            synced_contacts += 1
    return synced_contacts


def sync_contacts(fail_fast):
    """Synchronizes all WHMCS contacts for existing clients."""
    exception_list = []
    client_list = []
    for client in Client.objects.all():
        synced_account = SyncedAccount.objects.filter(client=client, subaccount=False).first()
        whmcs_client = Tblclients.objects.filter(
            id=synced_account.whmcs_id, uuid=synced_account.whmcs_uuid
        ).first() if synced_account else None
        if not whmcs_client and client.external_billing_id:
            whmcs_client = Tblclients.objects.filter(uuid=client.external_billing_id).first()

        if whmcs_client:
            try:
                synced_contacts = sync_client_contacts(fleio_client=client, whmcs_client=whmcs_client)
                client_list.append('Fleio client {} (ID: {}): Synced {} contact(s).'.format(client.name,
                                                                                            client.id,
                                                                                            synced_contacts))
            except Exception as ex:
                LOG.exception(ex)
                if fail_fast:
                    exception_list.append(ex)
                    break
                else:
                    exception_list.append(ex)
    return client_list, exception_list
