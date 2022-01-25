import decimal
import ipaddress

from django.db import transaction
from django.utils.timezone import now as utcnow

from fleio.billing.cart.serializers import OrderItemSerializer
from fleio.billing.models import CancellationRequest
from fleio.billing.models import ConfigurableOption
from fleio.billing.models import Product
from fleio.billing.models import ProductModule
from fleio.billing.models import Service
from fleio.billing.models import ServiceHostingAccount
from fleio.billing.models.calcelation_request import CancellationTypes
from fleio.billing.models.configurable_option import ConfigurableOptionWidget
from fleio.billing.models.product_cycle_periods import ProductCyclePeriods
from fleio.billing.service_cycle_manager import ServiceCycleManager
from fleio.billing.settings import ServiceStatus
from fleio.billing.settings import ServiceSuspendType
from fleio.core.models import Client
from fleio.core.models import Currency
from fleio.servers.models import Server
from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblcancelrequests
from whmcsync.whmcsync.models import Tblclients
from whmcsync.whmcsync.models import Tblhosting
from whmcsync.whmcsync.models import Tblhostingconfigoptions
from whmcsync.whmcsync.models import Tblproductconfigoptions
from whmcsync.whmcsync.models import Tblproductconfigoptionssub
from whmcsync.whmcsync.models import Tblproducts
from whmcsync.whmcsync.sync.utils import date_to_datetime
from whmcsync.whmcsync.utils import WHMCS_LOGGER

OPENSTACK_APP_LABEL = 'openstack'


def fleio_has_related_conf_opts(whmcs_service: Tblhosting):
    service_related_conf_opts = Tblhostingconfigoptions.objects.filter(relid=whmcs_service.id)
    fleio_has_all_options = True
    for service_related_conf_opt in service_related_conf_opts:
        if not fleio_has_all_options:
            break
        whmcs_related_conf_opt = Tblproductconfigoptions.objects.filter(id=service_related_conf_opt.configid).first()
        whmcs_related_conf_opt_choice = Tblproductconfigoptionssub.objects.filter(
            id=service_related_conf_opt.optionid,
            configid=service_related_conf_opt.configid,
        ).first()
        fleio_option = ConfigurableOption.objects.filter(name=whmcs_related_conf_opt.optionname).first()
        if fleio_option:
            if fleio_option.has_choices:
                fleio_has_all_options = fleio_option.choices.filter(
                    choice=whmcs_related_conf_opt_choice.optionname
                ).exists()
        else:
            fleio_has_all_options = False
    return fleio_has_all_options


def whmcs_service_to_client(whmcs_service: Tblhosting):
    synced_account = SyncedAccount.objects.filter(whmcs_id=whmcs_service.userid, subaccount=False).first()
    whmcs_client = Tblclients.objects.get(id=whmcs_service.userid)
    return synced_account.client if synced_account else Client.objects.filter(
        external_billing_id=whmcs_client.uuid
    ).first()


def whmcs_service_to_fleio_product(whmcs_service: Tblhosting):
    whmcs_product = Tblproducts.objects.get(pk=whmcs_service.packageid)
    if whmcs_product.servertype == 'fleio':
        openstack_module = ProductModule.objects.get(plugin__app_label=OPENSTACK_APP_LABEL)
        return Product.objects.filter(module=openstack_module).first()
    # retrieve synced product
    return Product.objects.filter(code='{}_{}_{}'.format('whmcs', whmcs_product.id, whmcs_product.gid)).first()


def get_fleio_product_cycle(whmcs_service: Tblhosting, currency: Currency) -> (str, int):
    fleio_product = whmcs_service_to_fleio_product(whmcs_service)
    cycle = None
    multiplier = None
    if whmcs_service.billingcycle.lower() == 'free account' or whmcs_service.amount < 0:
        return fleio_product.cycles.first()  # TODO(tomo): set the smallest cycle not the first
    elif whmcs_service.billingcycle.lower() == 'one time':
        cycle, multiplier = ProductCyclePeriods.onetime, 1
    elif whmcs_service.billingcycle.lower() == 'monthly':
        cycle, multiplier = ProductCyclePeriods.month, 1
    elif whmcs_service.billingcycle.lower() == 'quarterly':
        cycle, multiplier = ProductCyclePeriods.month, 3
    elif whmcs_service.billingcycle.lower() == 'semi-annually':
        cycle, multiplier = ProductCyclePeriods.month, 6
    elif whmcs_service.billingcycle.lower() == 'annually':
        cycle, multiplier = ProductCyclePeriods.year, 1
    elif whmcs_service.billingcycle.lower() == 'biennially':
        cycle, multiplier = ProductCyclePeriods.year, 2
    elif whmcs_service.billingcycle.lower() == 'triennially':
        cycle, multiplier = ProductCyclePeriods.year, 3
    cycle = fleio_product.cycles.get(cycle=cycle, cycle_multiplier=multiplier, currency=currency)
    return cycle


def get_fleio_service_status(whmcs_service: Tblhosting):
    """Match the WHMCS service status to the Fleio service status"""
    if whmcs_service.domainstatus.lower() == 'active':
        return ServiceStatus.active
    elif whmcs_service.domainstatus.lower() == 'suspended':
        return ServiceStatus.suspended
    elif whmcs_service.domainstatus.lower() == 'cancelled':
        return ServiceStatus.canceled
    elif whmcs_service.domainstatus.lower() == 'pending':
        return ServiceStatus.pending
    elif whmcs_service.domainstatus.lower() == 'fraud':
        return ServiceStatus.fraud
    elif whmcs_service.domainstatus.lower() == 'terminated':
        return ServiceStatus.terminated
    elif whmcs_service.domainstatus.lower() == 'completed':
        return ServiceStatus.archived
    else:
        return ServiceStatus.archived


def get_whmcs_service_internal_id(whmcs_service: Tblhosting):
    return 'whmcs_{}_{}'.format(whmcs_service.id, whmcs_service.userid)


def get_fleio_service_suspend_type(whmcs_service: Tblhosting, service_status):
    if service_status == ServiceStatus.suspended:
        if whmcs_service.suspendreason and whmcs_service.suspendreason.lower() == 'overdue on payment':
            return ServiceSuspendType.overdue
        return ServiceSuspendType.staff
    return None


def sync_cancellation_request_if_exists(whmcs_service: Tblhosting, fleio_service: Service):
    # NOTE(tomo): Get only the last cancellation request if exists
    cancellation_request = Tblcancelrequests.objects.filter(relid=whmcs_service.id).order_by('date').last()
    if cancellation_request:
        if not fleio_service.cancellation_request:
            cancellation_type = (CancellationTypes.IMMEDIATE if cancellation_request.type == 'Immediate' else
                                 CancellationTypes.END_OF_CYCLE)
            fleio_service.cancellation_request = CancellationRequest.objects.create(
                user=fleio_service.client.users.first(),
                created_at=cancellation_request.date,
                completed_at=date_to_datetime(whmcs_service.termination_date),
                reason=cancellation_request.reason[:2048],
                cancellation_type=cancellation_type
            )
            cancellation_request.save(update_fields=['cancellation_request'])
            WHMCS_LOGGER.info(
                'Created cancellation request for service {} ({})'.format(fleio_service.display_name, whmcs_service.id)
            )


def get_fleio_server_by_whmcs_id(whmcs_server_id):
    for server in Server.objects.all():
        if server.settings.get('id') == whmcs_server_id:
            return server


def sync_service_hosting_account(whmcs_service: Tblhosting, fleio_service: Service):
    # Sync server hosting account (domain and server)
    # The cPanel package name is taken from configoption1
    if not whmcs_service.server:
        return
    fleio_service_server = get_fleio_server_by_whmcs_id(whmcs_service.server)
    if not fleio_service_server:
        raise DBSyncException(
            'Cannot sync WHMCS service {} hosting account because related server {} was not found in fleio.'.format(
                whmcs_service.id, whmcs_service.server
            )
        )
    whmcs_product = Tblproducts.objects.get(pk=whmcs_service.packageid)
    if whmcs_service.dedicatedip:
        try:
            ipaddress.ip_address(whmcs_service.dedicatedip.strip())
            dedicated_ip = whmcs_service.dedicatedip.strip()
        except ValueError:
            WHMCS_LOGGER.error(
                'Unable to sync service {} IP: {}: Not a valid IP'.format(
                    whmcs_service.domain, whmcs_service.dedicatedip
                )
            )
            dedicated_ip = None
    else:
        dedicated_ip = None
    if whmcs_service.domain and whmcs_service.domain.strip():
        # Only create hosting accounts if domains are required for services
        # Otherwise come up with a way to determine the account_id for different WHMCS services
        ServiceHostingAccount.objects.update_or_create(server=fleio_service_server,
                                                       account_id=whmcs_service.domain,
                                                       service=fleio_service,
                                                       defaults={'username': whmcs_service.username,
                                                                 'password': whmcs_service.password,
                                                                 'dedicated_ip': dedicated_ip,
                                                                 'package_name': whmcs_product.configoption1})


def sync_service_conf_opts(whmcs_service: Tblhosting, fleio_service: Service):
    fleio_service.configurable_options.clear()
    for hosting_opt in Tblhostingconfigoptions.objects.filter(relid=whmcs_service.id):
        whmcs_option = Tblproductconfigoptions.objects.get(id=hosting_opt.configid)
        fleio_conf_option = ConfigurableOption.objects.filter(name=whmcs_option.optionname).first()
        if fleio_conf_option.widget == ConfigurableOptionWidget.yesno:
            option_value = 'yes' if hosting_opt.qty > 0 else 'no'
        elif fleio_conf_option.has_quantity:
            option_value = '{}'.format(hosting_opt.qty)
        else:
            option_value = ''
        if fleio_conf_option.has_choices:
            whmcs_choice = Tblproductconfigoptionssub.objects.get(id=hosting_opt.optionid)
            fleio_choice = fleio_conf_option.choices.filter(choice=whmcs_choice.optionname).first()
            option_value = fleio_choice.choice

        quantity = hosting_opt.qty if fleio_conf_option.has_quantity else 1  # Fleio needs 1 as quantity for all opts

        unit_price, price, setup_fee = fleio_conf_option.get_price_by_cycle_quantity_and_choice(
            cycle_name=fleio_service.cycle.cycle,
            cycle_multiplier=fleio_service.cycle.cycle_multiplier,
            currency=fleio_service.client.currency,
            quantity=quantity,
            choice_value=option_value if fleio_conf_option.has_choices else None,
            option_value=option_value,
        )

        fleio_service.configurable_options.create(
            option=fleio_conf_option,
            option_value=option_value,
            quantity=quantity,
            has_price=price > decimal.Decimal(0),
            taxable=fleio_service.product.taxable,
            price=price,
            unit_price=unit_price,
            setup_fee=setup_fee
        )
        WHMCS_LOGGER.info(
            'Synced configurable option {} for service {} ({})'.format(
                fleio_conf_option.name, fleio_service.display_name, whmcs_service.id
            )
        )


def sync_services(fail_fast, related_to_clients=None):
    exception_list = []
    skipped_list = []
    service_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    qs = Tblhosting.objects.exclude(packageid__lte=0)
    if related_to_clients:
        qs = qs.filter(userid__in=related_to_clients)
    for whmcs_service in qs:

        fleio_product = whmcs_service_to_fleio_product(whmcs_service=whmcs_service)
        if not fleio_product:
            WHMCS_LOGGER.warning(
                'Cannot sync whmcs service {} as Fleio related product is not imported'.format(whmcs_service.id)
            )
            skipped_list.append(whmcs_service.id)
            continue
        if fleio_product.module.plugin_label == OPENSTACK_APP_LABEL:
            WHMCS_LOGGER.debug(
                'Skipping syncing for service {} as it\'s related to a Fleio OpenStack product'.format(
                    whmcs_service.id
                )
            )
            # those are simply ignored, do not add in skipped services
            continue

        client = whmcs_service_to_client(whmcs_service=whmcs_service)
        if not client:
            WHMCS_LOGGER.warning(
                'Cannot sync whmcs service {} ({}) as Fleio related client (whmcs id: {}) is not imported'.format(
                    whmcs_service.id, whmcs_service.domain, whmcs_service.userid
                )
            )
            skipped_list.append(whmcs_service.id)
            continue

        if not fleio_has_related_conf_opts(whmcs_service=whmcs_service):
            WHMCS_LOGGER.warning(
                'Cannot sync whmcs service {} ({}) as Fleio related conf. options are not imported'.format(
                    whmcs_service.id, whmcs_service.domain,
                )
            )
            skipped_list.append(whmcs_service.id)
            continue

        WHMCS_LOGGER.debug('Syncing service: {}'.format(whmcs_service.domain or fleio_product.name))
        try:
            with transaction.atomic():
                product_cycle = get_fleio_product_cycle(whmcs_service=whmcs_service, currency=client.currency)
                internal_id = get_whmcs_service_internal_id(whmcs_service=whmcs_service)
                service_status = get_fleio_service_status(whmcs_service)
                override_suspend_until = date_to_datetime(whmcs_service.overidesuspenduntil)
                service_defaults = {
                    'display_name': fleio_product.name,
                    'status': service_status,
                    'notes': whmcs_service.notes[:4096],
                    'created_at': date_to_datetime(whmcs_service.regdate),
                    'terminated_at': date_to_datetime(whmcs_service.termination_date),
                    'suspend_reason': whmcs_service.suspendreason,
                    'override_suspend_until': override_suspend_until if (override_suspend_until and
                                                                         override_suspend_until > utcnow()) else None,
                    'is_free': (whmcs_service.billingcycle.lower() == 'free account' or
                                whmcs_service.amount < decimal.Decimal('0.00')),
                    'suspend_type': get_fleio_service_suspend_type(whmcs_service=whmcs_service,
                                                                   service_status=service_status),
                }

                service, created = Service.objects.update_or_create(
                    client=client,
                    product=fleio_product,
                    cycle=product_cycle,
                    internal_id=internal_id,
                    defaults=service_defaults,
                )

                if created:
                    ServiceCycleManager.create_initial_cycle(service=service, start_date=whmcs_service.nextduedate)

                sync_cancellation_request_if_exists(whmcs_service=whmcs_service, fleio_service=service)
                sync_service_hosting_account(whmcs_service=whmcs_service, fleio_service=service)
                sync_service_conf_opts(whmcs_service=whmcs_service, fleio_service=service)
                service_list.append(service.display_name)

        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            if created:
                WHMCS_LOGGER.info(
                    'Created service {} ({}) for client {}'.format(
                        service.display_name, whmcs_service.id, service.client.name
                    )
                )
            else:
                WHMCS_LOGGER.info(
                    'Updated service {} ({}) for client {}'.format(
                        service.display_name, whmcs_service.id, service.client.name
                    )
                )

    num_excluded = Tblhosting.objects.filter(packageid__lte=0).count()
    if num_excluded:
        WHMCS_LOGGER.warning('The following services without a product associated were excluded:')
        for excluded_service in Tblhosting.objects.filter(packageid__lte=0):
            WHMCS_LOGGER.warning(
                'ID: {} Domain: "{}" Billing cycle: {}'.format(
                    excluded_service.id, excluded_service.domain, excluded_service.billingcycle)
            )
    return service_list, exception_list, skipped_list
