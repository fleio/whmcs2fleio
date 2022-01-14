from django.db import transaction

from fleio.billing.models import Order
from fleio.billing.models import OrderItem
from fleio.billing.models import OrderItemConfigurableOption
from fleio.billing.models import OrderItemTypes
from fleio.billing.service_cycle_manager import ServiceCycleManager
from fleio.billing.service_manager import ServiceManager
from fleio.billing.settings import ServiceStatus
from fleio.core.models import Client
from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.models import SyncedAccount
from whmcsync.whmcsync.models import Tblclients
from whmcsync.whmcsync.models import Tblcontacts
from whmcsync.whmcsync.models import Tbldomains
from whmcsync.whmcsync.models import Tblorders
from whmcsync.whmcsync.utils import WHMCS_LOGGER

try:
    from plugins.domains.models import Domain
    from plugins.domains.models import TLD
    from plugins.domains.models.domain import DomainStatus
    from plugins.domains.models import Nameserver
    from plugins.domains.models import Registrar
    from plugins.domains.models import Contact
except (ImportError, RuntimeError):
    Domain = None
    TLD = None
    DomainStatus = None
    Nameserver = None
    Registrar = None
    Contact = None


def match_tld(whmcs_domain: Tbldomains):
    split_domain = whmcs_domain.domain.split('.')
    tld = split_domain[1]
    return TLD.objects.get(name='.{}'.format(tld))


def match_domain_status(whmcs_domain: Tbldomains):
    if whmcs_domain.status == 'Cancelled':
        return DomainStatus.cancelled
    elif whmcs_domain.status == 'Pending' or whmcs_domain.status == 'Pending Registration':
        return DomainStatus.pending
    elif whmcs_domain.status == 'Pending Transfer':
        return DomainStatus.pending_transfer
    elif whmcs_domain.status == 'Active':
        return DomainStatus.active
    elif whmcs_domain.status == 'Grace':
        return DomainStatus.grace
    elif whmcs_domain.status == 'Redemption':
        return DomainStatus.redemption
    elif whmcs_domain.status == 'Expired':
        return DomainStatus.expired
    elif whmcs_domain.status == 'Transferred Away':
        return DomainStatus.transferred_away
    elif whmcs_domain.status == 'Fraud':
        return DomainStatus.fraud
    return DomainStatus.undefined


def domain_status_to_service_status(whmcs_domain: Tbldomains):
    if whmcs_domain.status == 'Active':
        return ServiceStatus.active
    elif whmcs_domain.status == 'Cancelled':
        return ServiceStatus.canceled
    elif (whmcs_domain.status == 'Pending' or whmcs_domain.status == 'Pending Registration' or
          whmcs_domain.status == 'Pending Transfer'):
        return ServiceStatus.pending
    elif whmcs_domain.status == 'Expired':
        return ServiceStatus.terminated
    elif whmcs_domain.status == 'Fraud':
        return ServiceStatus.fraud
    return ServiceStatus.active


def match_registrar(whmcs_domain: Tbldomains):
    if not whmcs_domain.registrar:
        return None
    try:
        return Registrar.objects.get(name=whmcs_domain.registrar)
    except Registrar.DoesNotExist:
        WHMCS_LOGGER.error(
            'Cannot sync domain {} because related registrar not found in Fleio'.format(whmcs_domain.domain)
        )
        raise


def match_client(user_id):
    synced_account = SyncedAccount.objects.filter(whmcs_id=user_id, subaccount=False).first()
    whmcs_client = Tblclients.objects.get(id=user_id)
    return synced_account.client if synced_account else Client.objects.filter(
        external_billing_id=whmcs_client.uuid
    ).first()


# noinspection DuplicatedCode
def create_service_for_domain(domain_order_item: OrderItem, whmcs_domain: Tbldomains):
    service = ServiceManager.create_service(
        client=domain_order_item.order.client,
        display_name=domain_order_item.name,
        product=domain_order_item.product,
        product_cycle=domain_order_item.cycle,
        status=domain_status_to_service_status(whmcs_domain=whmcs_domain),
        plugin_data=domain_order_item.plugin_data,
        domain_name=domain_order_item.domain_name,
        initialize_after_create=False,
    )
    for config_option in domain_order_item.configurable_options.all():
        service.configurable_options.create(option=config_option.option,
                                            option_value=config_option.option_value,
                                            quantity=config_option.quantity,
                                            has_price=config_option.has_price,
                                            taxable=config_option.taxable,
                                            price=config_option.price,
                                            unit_price=config_option.unit_price,
                                            setup_fee=config_option.setup_fee)

    return service


def sync_domains(fail_fast, related_to_clients=None):
    exception_list = []
    domains_list = []
    qs = Tbldomains.objects.all()
    if related_to_clients:
        qs = qs.filter(userid__in=related_to_clients)
    for whmcs_domain in qs:
        try:
            with transaction.atomic():
                tld = match_tld(whmcs_domain=whmcs_domain)
                defaults = dict(
                    status=match_domain_status(whmcs_domain=whmcs_domain),
                    last_registrar=match_registrar(whmcs_domain=whmcs_domain),
                    registration_date=whmcs_domain.registrationdate,
                    expiry_date=whmcs_domain.expirydate,
                    registration_period=whmcs_domain.registrationperiod,
                )
                if whmcs_domain.created_at:
                    defaults['created_at'] = whmcs_domain.created_at
                if whmcs_domain.updated_at:
                    defaults['updated_at'] = whmcs_domain.updated_at

                fleio_domain, created = Domain.objects.update_or_create(
                    name=whmcs_domain.domain,
                    tld=match_tld(whmcs_domain=whmcs_domain),
                    defaults=defaults,
                )

                client = match_client(whmcs_domain.userid)  # type: Client
                if not client:
                    raise DBSyncException(
                        'Cannot import domain {} as related client is not found in Fleio.'.format(whmcs_domain.domain)
                    )

                if created and whmcs_domain.type == 'Register':
                    cycle = tld.register_product.cycles.filter(
                        currency=client.currency,
                        cycle_multiplier=whmcs_domain.registrationperiod,
                    ).first()

                    dns_cycle = tld.dns_option.cycles.filter(
                        currency=client.currency,
                        cycle_multiplier=whmcs_domain.registrationperiod,
                    ).first() if whmcs_domain.dnsmanagement else None

                    email_cycle = tld.email_option.cycles.filter(
                        currency=client.currency,
                        cycle_multiplier=whmcs_domain.registrationperiod,
                    ).first() if whmcs_domain.emailforwarding else None

                    id_cycle = tld.id_option.cycles.filter(
                        currency=client.currency,
                        cycle_multiplier=whmcs_domain.registrationperiod,
                    ).first() if whmcs_domain.idprotection else None

                    plugin_data = dict(
                        operation='register',
                        name=whmcs_domain.domain,
                    )

                    order = Order(client=client)  # dummy order & items to help us create the service
                    order_item = OrderItem(
                        order=order,
                        item_type=OrderItemTypes.service,
                        product=tld.register_product,
                        cycle=cycle,
                        fixed_price=cycle.fixed_price,
                        cycle_display=cycle.display_name,
                        plugin_data=plugin_data,
                        name=whmcs_domain.domain,
                        description='Domain registration',
                    )
                    if dns_cycle:
                        OrderItemConfigurableOption(
                            order_item=order_item,
                            option=tld.dns_option,
                            option_value="yes",
                            quantity=1,
                            has_price=True,
                            unit_price=dns_cycle.price,
                            price=dns_cycle.price,
                            setup_fee=0
                        )

                    if email_cycle:
                        OrderItemConfigurableOption(
                            order_item=order_item,
                            option=tld.email_option,
                            option_value="yes",
                            quantity=1,
                            has_price=True,
                            unit_price=email_cycle.price,
                            price=email_cycle.price,
                            setup_fee=0
                        )

                    if id_cycle:
                        OrderItemConfigurableOption(
                            order_item=order_item,
                            option=tld.id_option,
                            option_value="yes",
                            quantity=1,
                            has_price=True,
                            unit_price=id_cycle.price,
                            price=id_cycle.price,
                            setup_fee=0
                        )

                    service = create_service_for_domain(domain_order_item=order_item, whmcs_domain=whmcs_domain)
                    fleio_domain.service = service
                    fleio_domain.save(update_fields=['service'])

                    ServiceCycleManager.create_initial_cycle(service=service, start_date=whmcs_domain.nextduedate)

                    # add other relevant domain data from WHMCS order
                    related_whmcs_order = Tblorders.objects.get(id=whmcs_domain.orderid)
                    if related_whmcs_order.nameservers:
                        for nameserver in related_whmcs_order.nameservers.split(','):
                            nameserver = nameserver.strip()
                            if nameserver:
                                defaults = {'host_name': nameserver}
                                db_nameserver, created = Nameserver.objects.get_or_create(**defaults, defaults=defaults)
                                fleio_domain.nameservers.add(db_nameserver)

                    if related_whmcs_order.contactid:
                        whmcs_contact = Tblcontacts.objects.get(id=related_whmcs_order.contactid)
                        fleio_contact = Contact.objects.filter(client=client, email=whmcs_contact.email).first()
                        if not fleio_contact:
                            raise DBSyncException(
                                'Cannot sync domain {} because Fleio is missing related contact.'.format(
                                    whmcs_domain.domain
                                )
                            )
                        else:
                            fleio_domain.contact = fleio_contact
                            fleio_domain.save(update_fields=['contact'])

        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            domains_list.append(fleio_domain)
            if created:
                WHMCS_LOGGER.info('Created domain {}'.format(fleio_domain.name))
            else:
                WHMCS_LOGGER.info('Updated domain {}'.format(fleio_domain.name))
    return domains_list, exception_list
