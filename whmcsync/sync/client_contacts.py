import logging

from fleio.core.models import AppUser
from fleio.core.models import Client
from fleio.core.models import UserToClient
from plugins.domains.models import Contact
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblclients
from ..models import Tblcontacts

LOG = logging.getLogger('whmcsync')


def sync_client_contacts(fleio_client: Client, whmcs_client: Tblclients):
    """Place client contacts in client domain contacts and create additional users if contacts have sub accounts"""
    for wcontact in Tblcontacts.objects.filter(userid=whmcs_client.id):
        try:
            SyncedAccount.objects.get(whmcs_id=whmcs_client.id, whmcs_uuid=whmcs_client.uuid)
        except SyncedAccount.DoesNotExist:
            LOG.debug('Skip contact {} for {}. Client not synced'.format(wcontact.firstname, whmcs_client.firstname))
            continue
        contact, created = Contact.objects.update_or_create(client=fleio_client,
                                                            email=wcontact.email,
                                                            defaults={'first_name': wcontact.firstname,
                                                                      'last_name': wcontact.lastname,
                                                                      'company': wcontact.companyname,
                                                                      'address1': wcontact.address1,
                                                                      'address2': wcontact.address2,
                                                                      'city': wcontact.city,
                                                                      'country': wcontact.country,
                                                                      'state': wcontact.state,
                                                                      'zip_code': wcontact.postcode,
                                                                      'phone': wcontact.phonenumber})
        if not created:
            LOG.info('Updated contact {} for {}'.format(contact.name, contact.client.name))
        else:
            LOG.info('Created contact {} for {}'.format(contact.name, contact.client.name))

        if wcontact.subaccount:
            # NOTE(tomo): Create a new user and associate it with the Client this contact belongs to
            user, created = AppUser.objects.update_or_create(username=wcontact.email,
                                                             email=wcontact.email,
                                                             defaults={'first_name': wcontact.firstname,
                                                                       'last_name': wcontact.lastname,
                                                                       'password': wcontact.password,
                                                                       'is_active': True})
            if created:
                SyncedAccount.objects.create(whmcs_id=wcontact.id,
                                             user=user,
                                             client=fleio_client,
                                             password_synced=False,
                                             subaccount=True)
                UserToClient.objects.create(user=user, client=fleio_client)
                LOG.info('Created contact subaccount {} for {}'.format(user.email, fleio_client.long_name))
            else:
                LOG.info('Updated contact subaccount {} for {}'.format(user.email, fleio_client.long_name))
    return ''

