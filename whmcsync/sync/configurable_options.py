import decimal

from django.db import transaction

from fleio.billing.cart.serializers import QuantityWidgetSettingsSerializer
from fleio.billing.models import ConfigurableOption
from fleio.billing.models import ConfigurableOptionChoice
from fleio.billing.models import Product
from fleio.billing.models import ProductConfigurableOption
from fleio.billing.models.configurable_option import ConfigurableOptionCyclePriceType
from fleio.billing.models.configurable_option import ConfigurableOptionStatus
from fleio.billing.models.configurable_option import ConfigurableOptionWidget
from fleio.billing.models.product_cycle_periods import ProductCyclePeriods
from fleio.core.models import Currency
from .utils import get_whmcs_price
from ..exceptions import DBSyncException
from ..models import Tblcurrencies
from ..models import Tblpricing
from ..models import Tblproductconfiglinks
from ..models import Tblproductconfigoptions
from ..models import Tblproductconfigoptionssub
from ..models import Tblproducts
from ..utils import WHMCS_LOGGER


WIDGET_MAPPING = {
    '1': ConfigurableOptionWidget.dropdown,
    '2': ConfigurableOptionWidget.radio,
    '3': ConfigurableOptionWidget.yesno,
    '4': ConfigurableOptionWidget.number_input,
}


def get_fleio_currency(whmcs_currency_id):
    whmcs_currency = Tblcurrencies.objects.get(id=whmcs_currency_id)
    return Currency.objects.get(code=whmcs_currency.code)


def match_widget(whmcs_type: str):
    fleio_widget = WIDGET_MAPPING.get(whmcs_type, None)
    if not fleio_widget:
        raise DBSyncException('Cannot match configurable option type for whmcs type: {}'.format(whmcs_type))
    return fleio_widget


def sync_choices(fleio_conf_opt: ConfigurableOption, whmcs_conf_opt: Tblproductconfigoptions):
    if WIDGET_MAPPING.get(whmcs_conf_opt.optiontype) in ConfigurableOption.WIDGET_CHOICES.WITH_CHOICES:
        for whmcs_choice in Tblproductconfigoptionssub.objects.filter(configid=whmcs_conf_opt.id):
            ConfigurableOptionChoice.objects.update_or_create(
                option=fleio_conf_opt,
                choice=whmcs_choice.optionname,
                defaults=dict(
                    label=whmcs_choice.optionname,
                )
            )


def sync_product_options_links(fleio_conf_opt: ConfigurableOption, whmcs_conf_opt: Tblproductconfigoptions):
    whmcs_related_products = Tblproducts.objects.filter(
        id__in=Tblproductconfiglinks.objects.filter(gid=whmcs_conf_opt.gid).values_list('pid')
    )
    fleio_products = Product.objects.filter(name__in=list(whmcs_related_products.values_list('name', flat=True)))
    if whmcs_related_products.count() != fleio_products.count():
        WHMCS_LOGGER.warning(
            'Not all linked WHMCS products are imported for Fleio conf. option {} ({}).'.format(
                fleio_conf_opt.name, fleio_conf_opt.id
            )
        )
    ProductConfigurableOption.objects.filter(configurable_option=fleio_conf_opt).exclude(
        product__in=fleio_products
    ).delete()
    for fleio_product in fleio_products:
        product_configurable_option, created = ProductConfigurableOption.objects.get_or_create(
            product=fleio_product,
            configurable_option=fleio_conf_opt
        )
        if not product_configurable_option.cycles_match():
            WHMCS_LOGGER.warning('Option cycles for product {} and configurable option {} do not match!'.format(
                fleio_product.name, fleio_conf_opt.name)
            )


def sync_option_pricing(fleio_conf_opt: ConfigurableOption, whmcs_conf_opt: Tblproductconfigoptions):
    zero = decimal.Decimal('0.00')
    for whmcs_choice in Tblproductconfigoptionssub.objects.filter(configid=whmcs_conf_opt.id):
        fleio_choice = None
        if fleio_conf_opt.has_choices:
            fleio_choice = fleio_conf_opt.choices.filter(choice=whmcs_choice.optionname).first()

        whmcs_pricing = Tblpricing.objects.filter(type='configoptions', relid=whmcs_choice.id).all()  # multi currency

        for whmcs_price in whmcs_pricing:
            if whmcs_price.monthly >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.month,
                    value=fleio_choice,
                    cycle_multiplier=1,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.monthly),
                        setup_fee=get_whmcs_price(whmcs_price.msetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )
            if whmcs_price.quarterly >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.month,
                    value=fleio_choice,
                    cycle_multiplier=3,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.quarterly),
                        setup_fee=get_whmcs_price(whmcs_price.qsetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )
            if whmcs_price.semiannually >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.month,
                    value=fleio_choice,
                    cycle_multiplier=6,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.semiannually),
                        setup_fee=get_whmcs_price(whmcs_price.ssetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )
            if whmcs_price.annually >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.year,
                    value=fleio_choice,
                    cycle_multiplier=1,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.annually),
                        setup_fee=get_whmcs_price(whmcs_price.asetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )
            if whmcs_price.biennially >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.year,
                    value=fleio_choice,
                    cycle_multiplier=2,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.biennially),
                        setup_fee=get_whmcs_price(whmcs_price.bsetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )
            if whmcs_price.triennially >= zero:
                fleio_conf_opt.cycles.update_or_create(
                    cycle=ProductCyclePeriods.year,
                    value=fleio_choice,
                    cycle_multiplier=3,
                    currency=get_fleio_currency(whmcs_price.currency),
                    defaults=dict(
                        price=get_whmcs_price(whmcs_price.triennially),
                        setup_fee=get_whmcs_price(whmcs_price.tsetupfee),
                        is_relative_price=False,
                        price_type=ConfigurableOptionCyclePriceType.fixed,
                        percentage_relative_to_options=False,
                    )
                )


def sync_configurable_options(fail_fast):
    exception_list = []
    opts_list = []
    for whmcs_conf_opt in Tblproductconfigoptions.objects.all().order_by('order'):
        try:
            if not whmcs_conf_opt.optionname:
                raise DBSyncException(
                    'Cannot sync WHMCS configurable option {} without name as Fleio does not support this.'.format(
                        whmcs_conf_opt.id
                    )
                )
            settings_data = dict()
            serialized_settings = QuantityWidgetSettingsSerializer(data=dict(
                min=whmcs_conf_opt.qtyminimum,
                max=whmcs_conf_opt.qtymaximum,
            ))
            if serialized_settings.is_valid(raise_exception=True):
                settings_data = serialized_settings.validated_data
            with transaction.atomic():
                fleio_conf_opt, created = ConfigurableOption.objects.update_or_create(
                    name=whmcs_conf_opt.optionname,
                    widget=match_widget(whmcs_type=whmcs_conf_opt.optiontype),
                    defaults=dict(
                        settings=settings_data,
                        description=whmcs_conf_opt.optionname,
                        status=(ConfigurableOptionStatus.private if whmcs_conf_opt.hidden else
                                ConfigurableOptionStatus.public),
                    )
                )

                sync_choices(fleio_conf_opt=fleio_conf_opt, whmcs_conf_opt=whmcs_conf_opt)
                sync_option_pricing(fleio_conf_opt=fleio_conf_opt, whmcs_conf_opt=whmcs_conf_opt)
                sync_product_options_links(fleio_conf_opt=fleio_conf_opt, whmcs_conf_opt=whmcs_conf_opt)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            opts_list.append(fleio_conf_opt)
            if created:
                WHMCS_LOGGER.info('Created configurable option {}'.format(fleio_conf_opt.name))
            else:
                WHMCS_LOGGER.info('Updated configurable option {}'.format(fleio_conf_opt.name))
    return opts_list, exception_list
