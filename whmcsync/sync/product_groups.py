from fleio.billing.models import ProductGroup
from ..models import Tblproductgroups
from ..models import Tblproducts
from ..utils import WHMCS_LOGGER


def sync_product_groups(fail_fast):
    exception_list = []
    name_list = []
    for group in Tblproductgroups.objects.all():
        fleio_products_count = Tblproducts.objects.filter(servertype='fleio', gid=group.id).count()
        if Tblproducts.objects.filter(gid=group.id).count() == fleio_products_count:
            # if group has only fleio related products, skip it
            WHMCS_LOGGER.debug('Skipping group {} as it contains only fleio related products.'.format(group.id))
            continue
        try:
            new_gr, created = ProductGroup.objects.update_or_create(name=group.name,
                                                                    defaults={'description': group.headline or '',
                                                                              'visible': True})
            name_list.append(group.name)
            if created:
                msg = 'New product group synced: {}'.format(group.name)
            else:
                msg = 'Product group {} updated'.format(group.name)
            WHMCS_LOGGER.info(msg)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list
