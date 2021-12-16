from django.db import transaction

from fleio.billing.models import Product
from fleio.billing.models import ProductGroup
from fleio.billing.models import ProductModule
from fleio.billing.models.service_cycle_constants import ServiceCycleBillingTypes
from fleio.billing.settings import PricingModel
from fleio.billing.settings import ProductAutoSetup
from fleio.billing.settings import ProductType
from fleio.billing.settings import PublicStatuses
from whmcsync.whmcsync.models import Tblproductgroups
from whmcsync.whmcsync.sync.product_cycles import sync_product_cycles
from .servers import get_fleio_server_group_by_whmcs_id
from ..models import Tblproducts
from ..utils import WHMCS_LOGGER

try:
    from plugins.cpanelserver.models import CpanelServerProductSettings
except ImportError:
    CpanelServerProductSettings = None


def sync_products(fail_fast):
    exception_list = []
    name_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_product in Tblproducts.objects.exclude(servertype='fleio'):
        try:
            with transaction.atomic():
                fleio_prod, created = Product.objects.update_or_create(
                    name=whmcs_product.name,
                    group=get_fleio_product_group(whmcs_product.gid),
                    module=get_fleio_product_module(whmcs_product=whmcs_product),
                    product_type=get_fleio_product_type(whmcs_type=whmcs_product.type),
                    code='{}_{}_{}'.format('whmcs', whmcs_product.id, whmcs_product.gid),
                    defaults={
                        'description': format_product_description(whmcs_product.description),
                        'taxable': whmcs_product.tax,
                        'status': get_fleio_product_status(whmcs_product),
                        'auto_setup': get_fleio_product_auto_setup(whmcs_product=whmcs_product),
                        'price_model': get_fleio_product_price_model(whmcs_product=whmcs_product),
                        'billing_type': ServiceCycleBillingTypes.prepaid}
                )
                name_list.append(fleio_prod.name)
                sync_cpanel_module_settings(fleio_product=fleio_prod, whmcs_product=whmcs_product)
                sync_product_cycles(fleio_product=fleio_prod, whmcs_product=whmcs_product)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list


def format_product_description(description: str):
    """Replace br with a new line and remove the other tags"""
    if description:
        description = description.replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '\n')
        description.replace('<strong>', '').replace('<strong/>', '')
        description.replace('<em>', '').replace('<em/>', '')
    return description


def get_fleio_product_status(whmcs_product):
    if whmcs_product.retired:
        return PublicStatuses.retired
    elif whmcs_product.hidden:
        return PublicStatuses.private
    else:
        return PublicStatuses.public


def get_fleio_product_group(whmcs_group_id):
    whmcs_group = Tblproductgroups.objects.get(pk=whmcs_group_id)
    return ProductGroup.objects.filter(name=whmcs_group.name).first()


def get_fleio_product_type(whmcs_type):
    if whmcs_type == 'hostingaccount' or whmcs_type == 'reselleraccount':
        return ProductType.hosting
    else:
        return ProductType.generic


def get_fleio_product_auto_setup(whmcs_product: Tblproducts):
    if whmcs_product.autosetup == 'order':
        return ProductAutoSetup.on_order
    elif whmcs_product.autosetup == 'payment':
        return ProductAutoSetup.on_first_payment
    elif whmcs_product.autosetup == 'on':
        return ProductAutoSetup.manual
    else:
        return ProductAutoSetup.disabled


def get_fleio_product_module(whmcs_product: Tblproducts):
    if whmcs_product.servertype == 'cpanel':
        # Find and set the cPanel module
        return ProductModule.objects.filter(plugin__app_label='cpanelserver').first()
    else:
        return ProductModule.objects.filter(plugin__app_label='todo').first()


def get_fleio_product_price_model(whmcs_product: Tblproducts):
    if whmcs_product.paytype == 'free':
        return PricingModel.free
    else:
        return PricingModel.fixed_and_dynamic


def sync_cpanel_module_settings(fleio_product: Product, whmcs_product: Tblproducts):
    if whmcs_product.servertype == 'cpanel':
        if not CpanelServerProductSettings:
            return
        server_group = get_fleio_server_group_by_whmcs_id(server_group_id=whmcs_product.servergroup)
        module_settings, created = CpanelServerProductSettings.objects.update_or_create(
            product=fleio_product,
            defaults={
                'default_plan': whmcs_product.configoption1,
                'server_group': server_group}
        )
        WHMCS_LOGGER.debug(
            'Synced cPanel settings for {} plan: {} server group: {}'.format(
                fleio_product.name, module_settings.default_plan, server_group.name
            )
        )
