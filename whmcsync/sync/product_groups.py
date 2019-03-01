import logging

from django.utils.translation import ugettext_lazy as _

from fleio.billing.models import ProductGroup
from ..models import Tblproductgroups

LOG = logging.getLogger('whmcsync')


def sync_product_groups(fail_fast):
    exception_list = []
    name_list = []
    for group in Tblproductgroups.objects.all():
        try:
            new_gr, created = ProductGroup.objects.update_or_create(name=group.name,
                                                                    defaults={'description': group.headline or '',
                                                                              'visible': True})
            name_list.append(group.name)
            if created:
                msg = _('New product group synced: {}').format(group.name)
            else:
                msg = _('Product group {} updated').format(group.name)
            LOG.debug(msg)
        except Exception as e:
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list
