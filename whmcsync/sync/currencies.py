from django.db import transaction

from fleio.core.models import Currency
from whmcsync.whmcsync.models import Tblcurrencies
from whmcsync.whmcsync.utils import WHMCS_LOGGER


def sync_currencies(fail_fast, default=False):
    exception_list = []
    currency_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_currency in Tblcurrencies.objects.all():
        try:
            with transaction.atomic():
                fleio_currency, created = Currency.objects.update_or_create(code=whmcs_currency.code)
                if default:
                    if whmcs_currency.default:
                        fleio_currency.is_default = True
                        fleio_currency.rate = whmcs_currency.rate
                        fleio_currency.save(update_fields=['is_default', 'rate'])
                currency_list.append(fleio_currency)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            if created:
                WHMCS_LOGGER.info('Created currency {} with rate {}'.format(whmcs_currency.code, fleio_currency.rate))
            else:
                WHMCS_LOGGER.info('Updated currency {} with rate {}'.format(whmcs_currency.code, fleio_currency.rate))
    return currency_list, exception_list


