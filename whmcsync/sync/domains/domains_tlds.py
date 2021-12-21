from django.db import transaction

from .domains_registrars import WHMCS_REGISTRAR_TO_FLEIO_CONNECTOR
from whmcsync.whmcsync.models import Tblcurrencies
from whmcsync.whmcsync.models import Tblpricing
from whmcsync.whmcsync.models.tbldomainpricing import Tbldomainpricing
from whmcsync.whmcsync.utils import WHMCS_LOGGER
try:
    from plugins.domains.models import TLD
    from plugins.domains.utils.tld_pricing import save_tld_pricing
    from plugins.domains.models.tld import PriceType
    from plugins.domains.models import Registrar
    from plugins.domains.models import RegistrarConnector
except (ImportError, RuntimeError):
    TLD = None
    save_tld_pricing = None
    PriceType = None
    Registrar = None
    RegistrarConnector = None


PRICE_TYPE_MAP = {
    'domainregister': 'register',
    'domaintransfer': 'transfer',
    'domainrenew': 'renew'
}

PRICE_TIMESPAN_MAP = {
    1: 'msetupfee',
    2: 'qsetupfee',
    3: 'ssetupfee',
    4: 'asetupfee',
    5: 'bsetupfee',
    6: 'monthly',
    7: 'quarterly',
    8: 'semiannually',
    9: 'annually',
    10: 'biennially',
}


def match_registrar(whmcs_domain: Tbldomainpricing):
    if not whmcs_domain.autoreg:
        return None
    fleio_connector = RegistrarConnector.objects.filter(
        class_name=WHMCS_REGISTRAR_TO_FLEIO_CONNECTOR.get(
            whmcs_domain.autoreg, 'TODORegistrarConnector'
        )
    ).first()
    return Registrar.objects.get(
        connector=fleio_connector
    )


def import_tld_pricing(fleio_tld: TLD, whmcs_domain: Tbldomainpricing):
    domain_prices = dict(
        price_cycles_list=list(),
        price_types=PriceType.price_type_map
    )

    for whmcs_pricing in Tblpricing.objects.filter(
        relid=whmcs_domain.id,
        type__in=['domainregister', 'domaintransfer', 'domainrenew'],
    ):
        whmcs_currency = Tblcurrencies.objects.get(id=whmcs_pricing.currency)
        price_type = PRICE_TYPE_MAP.get(whmcs_pricing.type)
        prices_per_years = []
        for x in range(1, 11):
            prices_per_years.append(getattr(whmcs_pricing, PRICE_TIMESPAN_MAP[x], None))
        domain_prices['price_cycles_list'].append(
            dict(
                currency=dict(code=whmcs_currency.code),
                currency_code=whmcs_currency.code,
                price_type=price_type,
                prices_per_years=prices_per_years,
                relative_prices=False,
            )
        )
    save_tld_pricing(tld=fleio_tld, domain_prices=domain_prices, domain_addon_prices=None)


def sync_tlds(fail_fast):
    exception_list = []
    tld_list = []
    for whmcs_domain in Tbldomainpricing.objects.all():
        try:
            with transaction.atomic():
                defaults = dict(
                    default_registrar=match_registrar(whmcs_domain=whmcs_domain)
                )
                if whmcs_domain.updated_at:
                    defaults['updated_at'] = whmcs_domain.updated_at
                if whmcs_domain.created_at:
                    defaults['created_at'] = whmcs_domain.created_at
                fleio_tld, created = TLD.objects.update_or_create(
                    name=whmcs_domain.extension,
                    defaults=defaults,
                )
                import_tld_pricing(fleio_tld=fleio_tld, whmcs_domain=whmcs_domain)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            tld_list.append(fleio_tld)
            if created:
                WHMCS_LOGGER.info('Created TLD {}'.format(fleio_tld.name))
            else:
                WHMCS_LOGGER.info('Updated TLD {}'.format(fleio_tld.name))
    return tld_list, exception_list

