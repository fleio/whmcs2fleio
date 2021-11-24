import logging

from django.utils.translation import ugettext_lazy as _

from fleio.core.models import Currency
from whmcsync.whmcsync.models import Tblcurrencies

LOG = logging.getLogger('whmcsync')


def sync_currencies(fail_fast, default=False):
    exception_list = []
    currency_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_currency in Tblcurrencies.objects.all():
        try:
            fleio_currency, created = Currency.objects.update_or_create(code=whmcs_currency.code)
            if default:
                if whmcs_currency.default:
                    fleio_currency.is_default = True
                    fleio_currency.rate = whmcs_currency.rate
                    fleio_currency.save(update_fields=['is_default', 'rate'])
            currency_list.append(fleio_currency)
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            if created:
                LOG.info(_('Created currency {} with rate {}').format(whmcs_currency.code, fleio_currency.rate))
            else:
                LOG.info(_('Updated currency {} with rate {}').format(whmcs_currency.code, fleio_currency.rate))
    return currency_list, exception_list


