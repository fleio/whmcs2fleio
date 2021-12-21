from django.db import transaction

from whmcsync.whmcsync.models.tblregistrars import Tblregistrars
from whmcsync.whmcsync.utils import WHMCS_LOGGER
try:
    from plugins.domains.models import Registrar
    from plugins.domains.models import RegistrarConnector
except (ImportError, RuntimeError):
    Registrar = None
    RegistrarConnector = None


WHMCS_REGISTRAR_TO_FLEIO_CONNECTOR = {
    'openprovider': 'OpenproviderConnector',
    'resellerclub': 'ResellerclubConnector',
    'rotld': 'RotldConnector',
}


def sync_domain_registrars(fail_fast):
    exception_list = []
    registrars_list = []
    processed_registrars = []
    for whmcs_registrar in Tblregistrars.objects.all():
        try:
            if whmcs_registrar.registrar in processed_registrars:
                continue
            with transaction.atomic():
                fleio_connector = RegistrarConnector.objects.filter(
                    class_name=WHMCS_REGISTRAR_TO_FLEIO_CONNECTOR.get(
                        whmcs_registrar.registrar, 'TODORegistrarConnector'
                    )
                ).first()
                if not fleio_connector:
                    WHMCS_LOGGER.warning(
                        'Could not find a connector for registrar {}'.format(whmcs_registrar.registrar)
                    )
                fleio_registrar, created = Registrar.objects.update_or_create(
                    name=whmcs_registrar.registrar,
                    defaults=dict(
                        connector=fleio_connector,
                    ),
                )
                processed_registrars.append(whmcs_registrar.registrar)
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            registrars_list.append(whmcs_registrar)
            if created:
                WHMCS_LOGGER.info('Created registrar {}'.format(fleio_registrar.name))
            else:
                WHMCS_LOGGER.info('Updated registrar {}'.format(fleio_registrar.name))
    return registrars_list, exception_list

