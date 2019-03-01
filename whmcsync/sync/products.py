import logging

from fleio.billing.models import Product
from fleio.billing.models import ProductGroup
from fleio.billing.models import ProductModule
from fleio.billing.settings import PricingModel
from fleio.billing.settings import ProductAutoSetup
from fleio.billing.settings import ProductType
from fleio.billing.settings import PublicStatuses
from fleio.servers.models import Server
from fleio.servers.models import ServerGroup
from whmcsync.whmcsync.models import Tblproductgroups
from whmcsync.whmcsync.models import Tblservergroups
from whmcsync.whmcsync.sync.product_cycles import sync_product_cycles
from whmcsync.whmcsync.sync.servers import DEFAULT_UNKNOWN_GROUP
from ..models import Tblproducts

try:
    from plugins.cpanelserver.models import CpanelServerProductSettings
except ImportError:
    CpanelServerProductSettings = None

LOG = logging.getLogger('whmcsync')


def sync_products(fail_fast):
    exception_list = []
    name_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_product in Tblproducts.objects.exclude(servertype='fleio'):
        try:
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
                    'has_quantity': whmcs_product.stockcontrol,
                    'available_quantity': whmcs_product.qty,
                    'price_model': get_fleio_product_price_model(whmcs_product=whmcs_product)}
            )
            name_list.append(fleio_prod.name)
            sync_cpanel_module_settings(fleio_product=fleio_prod, whmcs_product=whmcs_product)
            sync_hypanel_module_settings(fleio_product=fleio_prod, whmcs_product=whmcs_product)
            sync_product_cycles(fleio_product=fleio_prod, whmcs_product=whmcs_product)
        except Exception as e:
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
    elif whmcs_product.servertype == 'hypanel':
        # Find and set the Hypanel module
        return ProductModule.objects.filter(plugin__app_label='hypanel').first()
    else:
        return ProductModule.objects.filter(plugin__app_label='todo').first()


def get_fleio_product_price_model(whmcs_product: Tblproducts):
    if whmcs_product.paytype == 'free':
        return PricingModel.free
    else:
        return PricingModel.fixed_and_dynamic


def get_fleio_cpanel_server_group(whmcs_product: Tblproducts):
    """We only support one server in one group for now"""
    if not whmcs_product.servergroup:
        return ServerGroup.objects.get(name=DEFAULT_UNKNOWN_GROUP)
    try:
        whmcs_group = Tblservergroups.objects.get(id=whmcs_product.servergroup)
    except Tblproductgroups.DoesNotExist:
        # NOTE: the group does not exist anymore, use the default group
        return ServerGroup.objects.get(name=DEFAULT_UNKNOWN_GROUP)
    return ServerGroup.objects.get(name=whmcs_group.name)


def sync_cpanel_module_settings(fleio_product: Product, whmcs_product: Tblproducts):
    if whmcs_product.servertype == 'cpanel':
        if not CpanelServerProductSettings:
            return
        server_group = get_fleio_cpanel_server_group(whmcs_product=whmcs_product)
        module_settings, created = CpanelServerProductSettings.objects.update_or_create(
            product=fleio_product,
            defaults={
                'default_plan': whmcs_product.configoption1,
                'server_group': server_group}
        )
        LOG.debug('Synced cPanel settings for {} plan: {} server group: {}'.format(fleio_product.name,
                                                                                   module_settings.default_plan,
                                                                                   server_group.name))


def sync_hypanel_module_settings(fleio_product: Product, whmcs_product: Tblproducts):
    if whmcs_product.servertype == 'hypanel':
        try:
            from plugins.hypanel.models import HypanelProductSettings
        except ImportError:
            return
        hypanel_server = Server.objects.filter(plugin__app_label='hypanel').first()  # Only one server exists like this
        HypanelProductSettings.objects.update_or_create(product=fleio_product,
                                                        defaults={
                                                            'hypanel_server': hypanel_server,
                                                            'configuration': whmcs_product.configoption7,
                                                            'ip_count': whmcs_product.configoption8,
                                                            'memory': whmcs_product.configoption2,
                                                            'disk_size': whmcs_product.configoption3,
                                                            'traffic': whmcs_product.configoption4,
                                                            'send_welcome_email': whmcs_product.configoption5 == 'on',
                                                            'server_group': whmcs_product.configoption6
                                                        })
        LOG.debug('Synced Hypanel setting for {} plan: {}'.format(fleio_product.name, whmcs_product.configoption7))
