import logging

from django.utils.translation import ugettext_lazy as _

from fleio.core.models import ClientGroup
from ..models import Tblclientgroups

LOG = logging.getLogger('whmcsync')


def sync_client_groups(options):
    fail_fast = options.get('failfast', False)
    exception_list = []
    name_list = []
    for group in Tblclientgroups.objects.all():
        try:
            new_gr, created = ClientGroup.objects.update_or_create(name=group.groupname,
                                                                   defaults={'description': 'WHMCS Client Group'})
            name_list.append(group.groupname)
            if created:
                msg = _('New client group synced: {}').format(group.groupname)
            else:
                msg = _('Client group "{}" updated').format(group.groupname)
            LOG.debug(msg)
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list
