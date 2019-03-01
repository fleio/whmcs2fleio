import logging

from django.utils.translation import ugettext_lazy as _

from fleio.billing.models import TaxRule
from ..models import Tbltax

LOG = logging.getLogger('whmcsync')


def sync_tax_rules(fail_fast):
    exception_list = []
    tax_list = []
    # NOTE: filter all products except for fleio products, for cases when the WHMCS module was used
    for whmcs_tax in Tbltax.objects.all():
        try:
            fleio_tax, created = TaxRule.objects.update_or_create(level=whmcs_tax.level,
                                                                  state=whmcs_tax.state or None,
                                                                  country=whmcs_tax.country,
                                                                  defaults={'rate': whmcs_tax.taxrate,
                                                                            'name': whmcs_tax.name})
        except Exception as e:
            exception_list.append(e)
            if fail_fast:
                break
        else:
            if created:
                LOG.info(_('Created tax {} for {}: {}%').format(fleio_tax.name, fleio_tax.country, fleio_tax.rate))
            else:
                LOG.info(_('Updated tax {} for {}: {}%').format(fleio_tax.name, fleio_tax.country, fleio_tax.rate))
    return tax_list, exception_list

