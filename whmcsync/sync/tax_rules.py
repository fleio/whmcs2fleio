from fleio.billing.models import TaxRule
from ..models import Tbltax
from ..utils import WHMCS_LOGGER


def sync_tax_rules(fail_fast):
    exception_list = []
    tax_list = []
    skipped_list = []
    for whmcs_tax in Tbltax.objects.all():
        try:
            if not whmcs_tax.country:
                WHMCS_LOGGER.warning(
                    'Cannot sync WHMCS tax rule {} ({}) that applies to all countries because '
                    'Fleio does not support this scenario.'.format(whmcs_tax.name, whmcs_tax.id)
                )
                skipped_list.append(whmcs_tax)
                continue
            fleio_tax, created = TaxRule.objects.update_or_create(level=whmcs_tax.level,
                                                                  state=whmcs_tax.state or None,
                                                                  country=whmcs_tax.country,
                                                                  defaults={'rate': whmcs_tax.taxrate,
                                                                            'name': whmcs_tax.name})
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            tax_list.append(fleio_tax)
            if created:
                WHMCS_LOGGER.info('Created tax {} for {}: {}'.format(fleio_tax.name, fleio_tax.country, fleio_tax.rate))
            else:
                WHMCS_LOGGER.info('Updated tax {} for {}: {}'.format(fleio_tax.name, fleio_tax.country, fleio_tax.rate))
    return tax_list, exception_list, skipped_list

