import decimal

from fleio.billing.models.product_cycle_periods import ProductCyclePeriods
from fleio.billing.settings import PublicStatuses
from fleio.core.models import Currency
from whmcsync.whmcsync.models import Tblcurrencies
from whmcsync.whmcsync.models import Tblpricing


def get_whmcs_price(price):
    if decimal.Decimal(price) < decimal.Decimal('0.00'):
        return decimal.Decimal('0.00')
    else:
        return decimal.Decimal(price)


def get_whmcs_currency(currency_id):
    whmcs_currency = Tblcurrencies.objects.get(id=currency_id)
    return Currency.objects.get(code=whmcs_currency.code)


def sync_product_cycles(fleio_product, whmcs_product):
    zero = decimal.Decimal('0.00')
    if whmcs_product.paytype == 'free':
        return
    whmcs_pricing = Tblpricing.objects.filter(type='product', relid=whmcs_product.id).all()  # multi currency
    for whmcs_price in whmcs_pricing:
        if whmcs_product.paytype == 'ontime':
            fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.onetime,
                                                  cycle_multiplier=1,
                                                  currency=get_whmcs_currency(whmcs_price.currency),
                                                  defaults={
                                                      'setup_fee': get_whmcs_price(whmcs_price.msetupfee),
                                                      'fixed_price': get_whmcs_price(whmcs_price.monthly),
                                                      'is_relative_price': False,
                                                      'status': PublicStatuses.public})
        elif whmcs_product.paytype == 'recurring':
            # monthly, querterly, semin-anual, anual, bienal, trienal
            if whmcs_price.monthly >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.month,
                                                      cycle_multiplier=1,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.msetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.monthly),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public})
            if whmcs_price.quarterly >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.month,
                                                      cycle_multiplier=3,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.qsetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.quarterly),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public})
            if whmcs_price.semiannually >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.month,
                                                      cycle_multiplier=6,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.ssetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.semiannually),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public})
            if whmcs_price.annually >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.year,
                                                      cycle_multiplier=1,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.asetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.annually),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public}
                                                      )
            if whmcs_price.biennially >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.year,
                                                      cycle_multiplier=2,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.bsetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.biennially),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public}
                                                      )
            if whmcs_price.triennially >= zero:
                fleio_product.cycles.update_or_create(cycle=ProductCyclePeriods.year,
                                                      cycle_multiplier=3,
                                                      currency=get_whmcs_currency(whmcs_price.currency),
                                                      defaults={
                                                          'setup_fee': get_whmcs_price(whmcs_price.tsetupfee),
                                                          'fixed_price': get_whmcs_price(whmcs_price.triennially),
                                                          'is_relative_price': False,
                                                          'status': PublicStatuses.public}
                                                      )
