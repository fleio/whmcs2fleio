from fleio.core.models import ClientGroup
from ..models import Tblclientgroups
from ..utils import WHMCS_LOGGER


def sync_client_groups(fail_fast):
    exception_list = []
    name_list = []
    for group in Tblclientgroups.objects.all():
        try:
            new_gr, created = ClientGroup.objects.update_or_create(name=group.groupname,
                                                                   defaults={'description': 'WHMCS Client Group'})
            name_list.append(group.groupname)
            if created:
                msg = 'New client group synced: {}'.format(group.groupname)
            else:
                msg = 'Client group "{}" updated'.format(group.groupname)
            WHMCS_LOGGER.info(msg)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list
