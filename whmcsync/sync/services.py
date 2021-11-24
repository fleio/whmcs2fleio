import decimal
import ipaddress
import logging

from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now as utcnow

from fleio.billing.models import CancellationRequest
from fleio.billing.models import Product
from fleio.billing.models import Service
from fleio.billing.models import ServiceHostingAccount
from fleio.billing.models.calcelation_request import CancellationTypes
from fleio.billing.models.product_cycle_periods import ProductCyclePeriods
from fleio.billing.settings import ServiceStatus
from fleio.billing.settings import ServiceSuspendType
from fleio.core.models import Currency
from fleio.servers.models import Server
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblcancelrequests
from whmcsync.whmcsync.models import Tblhosting
from whmcsync.whmcsync.models import Tblproducts

LOG = logging.getLogger('whmcsync')
DEFAULT_OPENSTACK = 'default_openstack'


def sync_services(fail_fast):
    exception_list = []
    service_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_service in Tblhosting.objects.exclude(packageid__lte=0):
        synced_account = whmcs_service_to_synced_account(whmcs_service)
        fleio_product = whmcs_service_to_fleio_product(whmcs_service)
        if fleio_product.code == DEFAULT_OPENSTACK:
            # NOTE(tomo): Project should already exist
            continue
        client = synced_account.client
        currency = client.currency
        service_cycle = get_whmcs_service_cycle(whmcs_service=whmcs_service, currency=currency)
        internal_id = get_whmcs_service_internal_id(whmcs_service=whmcs_service)
        try:
            service_status = whmcs_service_status(whmcs_service)
            service_defaults = {'display_name': fleio_product.name,
                                'status': service_status,
                                'notes': whmcs_service.notes[:4096],
                                'created_at': date_to_datetime(whmcs_service.regdate)}
            if whmcs_service.billingcycle.lower() == 'free account' or whmcs_service.amount < decimal.Decimal('0.00'):
                # WHMCS services with Free cycles and/or negative amount should have an overriden price set to 0
                # since we don't have an other equivalent in Fleio
                service_defaults['override_price'] = decimal.Decimal('0.00')
            if whmcs_service.nextduedate:
                service_defaults['next_due_date'] = date_to_datetime(whmcs_service.nextduedate)
            if whmcs_service.nextinvoicedate:
                service_defaults['next_invoice_date'] = date_to_datetime(whmcs_service.nextinvoicedate)
            if whmcs_service.overidesuspenduntil:
                overide_datetime = date_to_datetime(whmcs_service.overidesuspenduntil)
                if overide_datetime > utcnow():
                    service_defaults['override_suspend_until'] = overide_datetime
            if whmcs_service.suspendreason:
                service_defaults['suspend_reason'] = whmcs_service.suspendreason
            if service_status == ServiceStatus.suspended:
                if whmcs_service.suspendreason and whmcs_service.suspendreason.lower() == 'overdue on payment':
                    service_defaults['suspend_type'] = ServiceSuspendType.overdue
                else:
                    service_defaults['suspend_type'] = ServiceSuspendType.staff
            if whmcs_service.termination_date:
                service_defaults['terminated_at'] = date_to_datetime(whmcs_service.termination_date)

            service, created = Service.objects.update_or_create(client=client,
                                                                product=fleio_product,
                                                                cycle=service_cycle,
                                                                internal_id=internal_id,
                                                                defaults=service_defaults)
            if created:
                sync_cancellation_request_if_exists(whmcs_service=whmcs_service, fleio_service=service)

            # Sync server hosting account (domain and server)
            # The cPanel package name is taken from configoption1
            fleio_service_server = get_fleio_server_by_whmcs_id(whmcs_service.server)
            whmcs_product = Tblproducts.objects.get(pk=whmcs_service.packageid)
            if whmcs_service.dedicatedip:
                try:
                    ipaddress.ip_address(whmcs_service.dedicatedip.strip())
                    dedicated_ip = whmcs_service.dedicatedip.strip()
                except ValueError as e:
                    exception_list.append(e)
                    LOG.error('Unable to sync service {} IP: {}: Not a valid IP'.format(whmcs_service.domain,
                                                                                        whmcs_service.dedicatedip))
                    dedicated_ip = None
            else:
                dedicated_ip = None
            if whmcs_service.domain and whmcs_service.domain.strip():
                # Only create hosting accounts if domains are required for services
                # Otherwise come up with a way to determine the account_id for different WHMCS services
                ServiceHostingAccount.objects.update_or_create(server=fleio_service_server,
                                                               account_id=whmcs_service.domain,
                                                               service=service,
                                                               defaults={'username': whmcs_service.username,
                                                                         'password': whmcs_service.password,
                                                                         'dedicated_ip': dedicated_ip,
                                                                         'package_name': whmcs_product.configoption1})

        except Exception as e:
            exception_list.append(e)
            if fail_fast:
                break

    num_excluded = Tblhosting.objects.filter(packageid__lte=0).count()
    if num_excluded:
        LOG.warning('The following services without a product associated were excluded:')
        for excluded_service in Tblhosting.objects.filter(packageid__lte=0):
            LOG.warning('ID: {} Domain: "{}" Billing cycle: {}'.format(excluded_service.id,
                                                                       excluded_service.domain,
                                                                       excluded_service.billingcycle))
    return service_list, exception_list


def get_whmcs_service_internal_id(whmcs_service: Tblhosting):
    return 'whmcs_{}_{}'.format(whmcs_service.id, whmcs_service.userid)


def whmcs_service_status(whmcs_service: Tblhosting):
    """Match the WHMCS service status to the Fleio service status"""
    if whmcs_service.domainstatus.lower() == 'active':
        return ServiceStatus.active
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


def whmcs_service_to_synced_account(whmcs_service: Tblhosting):
    synced_account = SyncedAccount.objects.get(whmcs_id=whmcs_service.userid, subaccount=False)
    return synced_account


def whmcs_service_to_fleio_product(whmcs_service: Tblhosting):
    whmcs_product = Tblproducts.objects.get(pk=whmcs_service.packageid)
    if whmcs_product.servertype == 'fleio':
        return Product.objects.get(code=DEFAULT_OPENSTACK)
    return Product.objects.get(code='{}_{}_{}'.format('whmcs', whmcs_product.id, whmcs_product.gid))


def get_whmcs_service_cycle(whmcs_service: Tblhosting, currency: Currency) -> (str, int):
    fleio_product = whmcs_service_to_fleio_product(whmcs_service)
    LOG.debug('Syncing service: {}'.format(whmcs_service.domain or fleio_product.name))
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
    ret_cycle = fleio_product.cycles.get(cycle=cycle, cycle_multiplier=multiplier, currency=currency)
    return ret_cycle


def sync_cancellation_request_if_exists(whmcs_service: Tblhosting, fleio_service: Service):
    c_req = None
    # NOTE(tomo): Get only the last cancellation request if exists
    cancellation_request = Tblcancelrequests.objects.filter(relid=whmcs_service.id).order_by('date').last()
    if not cancellation_request:
        return c_req
    else:
        if not fleio_service.cancellation_request:
            cancellation_type = (CancellationTypes.IMMEDIATE if cancellation_request.type == 'Immediate' else
                                 CancellationTypes.END_OF_CYCLE)
            if whmcs_service.termination_date:
                req_completed_at = date_to_datetime(whmcs_service.termination_date)
            else:
                req_completed_at = None
            c_req = CancellationRequest.objects.create(user=fleio_service.client.users.first(),
                                                       created_at=cancellation_request.date,
                                                       completed_at=req_completed_at,
                                                       reason=cancellation_request.reason,
                                                       cancellation_type=cancellation_type)
            fleio_service.cancellation_request = c_req
    return c_req


def get_fleio_server_by_whmcs_id(whmcs_server_id):
    for server in Server.objects.all():
        if server.settings.get('id') == whmcs_server_id:
            return server


def set_tz(date_time, tz=timezone.utc):
    return timezone.make_aware(date_time, timezone=tz)


def date_to_datetime(date):
    dt = datetime.combine(date, datetime.min.time())
    return set_tz(dt, tz=timezone.utc)
