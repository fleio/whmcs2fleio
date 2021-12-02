from django.utils.translation import ugettext_lazy as _

from common.logger import get_fleio_logger
from fleio.billing.models import ProductGroup
from ..models import Tblproductgroups
from ..models import Tblproducts

LOG = get_fleio_logger('whmcsync')


def sync_product_groups(fail_fast):
    exception_list = []
    name_list = []
    for group in Tblproductgroups.objects.all():
        fleio_products_count = Tblproducts.objects.filter(servertype='fleio', gid=group.id).count()
        if Tblproducts.objects.filter(gid=group.id).count() == fleio_products_count:
            # if group has only fleio related products, skip it
            LOG.debug('Skipping group {} as it contains only fleio related products.'.format(group.id))
            continue
        try:
            new_gr, created = ProductGroup.objects.update_or_create(name=group.name,
                                                                    defaults={'description': group.headline or '',
                                                                              'visible': True})
            name_list.append(group.name)
            if created:
                msg = _('New product group synced: {}').format(group.name)
            else:
                msg = _('Product group {} updated').format(group.name)
            LOG.info(msg)
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list
