from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from common.logger import get_fleio_logger
from fleio.conf.utils import fernet_encrypt
from fleio.core.models import Plugin
from fleio.servers.models import HostingServerSettings
from fleio.servers.models import Server
from fleio.servers.models import ServerGroup
from fleio.servers.models.server import ServerStatus
from .utils import FieldToSync
from .utils import sync_fields
from ..models import Tblservergroups
from ..models import Tblservergroupsrel
from ..models import Tblservers

LOG = get_fleio_logger('whmcsync')

DEFAULT_UNKNOWN_GROUP = 'WHMCS Unknown'


class HostingServerSettingField(FieldToSync):
    record_name = 'Hosting server setting'


SERVER_SETTINGS_FIELDS_TO_SYNC = [
    HostingServerSettingField(fleio_key='hostname', whmcs_key='hostname', fleio_max_length=255),
    HostingServerSettingField(fleio_key='username', whmcs_key='username', fleio_max_length=255),
    HostingServerSettingField(fleio_key='status_url', whmcs_key='statusaddress', fleio_max_length=255),
    HostingServerSettingField(fleio_key='api_token', whmcs_key='accesshash', fleio_max_length=4096, encrypt=True),
    HostingServerSettingField(fleio_key='assigned_ips', whmcs_key='assignedips', fleio_max_length=4096),
    HostingServerSettingField(fleio_key='port', whmcs_key='port', default=0),
    HostingServerSettingField(fleio_key='max_accounts', whmcs_key='maxaccounts'),
]


def sync_server_groups(options):
    fail_fast = options.get('failfast', False)
    exception_list = []
    name_list = []
    for group in Tblservergroups.objects.all():
        try:
            new_gr, created = ServerGroup.objects.update_or_create(name=group.name,
                                                                   defaults={'description': 'WHMCS server group'})
            name_list.append(group.name)
            if created:
                msg = _('New server group created: {}').format(group.name)
            else:
                msg = _('Server group "{}" updated').format(group.name)
            LOG.debug(msg)
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list


def sync_servers(options):
    fail_fast = options.get('failfast', False)
    exception_list = []
    name_list = []
    for whmcs_server in Tblservers.objects.all():
        try:
            with transaction.atomic():
                server, created = Server.objects.update_or_create(
                    name=whmcs_server.name,
                    group=get_fleio_server_group(whmcs_server=whmcs_server),
                    plugin=get_fleio_server_plugin(whmcs_server=whmcs_server),
                    defaults={'status': (ServerStatus.disabled if whmcs_server.disabled or
                                         not whmcs_server.active else ServerStatus.enabled),
                              'settings': get_fleio_server_settings(whmcs_server=whmcs_server)}
                )
                settings, created = HostingServerSettings.objects.get_or_create(server=server)
                settings.secure = True if whmcs_server.secure == 'on' else False
                sync_fields(
                    fleio_record=settings, whmcs_record=whmcs_server, fields_to_sync=SERVER_SETTINGS_FIELDS_TO_SYNC
                )
                settings.save()
                name_list.append(server.name)
        except Exception as e:
            LOG.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
    return name_list, exception_list


def get_fleio_server_group(whmcs_server: Tblservers):
    """We only support one server in one group for now"""
    group_rel = Tblservergroupsrel.objects.filter(serverid=whmcs_server.id).first()
    if not group_rel:
        unknown_gr, created = ServerGroup.objects.get_or_create(name=DEFAULT_UNKNOWN_GROUP,
                                                                description='Servers with WHMCS deleted groups')
        return unknown_gr
    whmcs_group = Tblservergroups.objects.get(id=group_rel.groupid)
    return ServerGroup.objects.get(name=whmcs_group.name)


def get_fleio_server_plugin(whmcs_server: Tblservers):
    whmcs_server_type = whmcs_server.type
    if whmcs_server_type == 'cpanel':
        return Plugin.objects.filter(app_label='cpanelserver').first()
    else:
        LOG.warning(
            'Fallback to Fleio TODO plugin (if exists) for server {} with server type {}'.format(whmcs_server.name,
                                                                                                 whmcs_server_type)
        )
        return Plugin.objects.filter(app_label='todo').first()


def get_fleio_server_settings(whmcs_server: Tblservers):
    server_settings = {'username': whmcs_server.username,
                       'hostname': whmcs_server.hostname,
                       'accesshash': whmcs_server.accesshash,
                       'password': whmcs_server.password,
                       'ipaddress': whmcs_server.ipaddress,
                       'assignedips': whmcs_server.assignedips,
                       'noc': whmcs_server.noc,
                       'statusaddress': whmcs_server.statusaddress,
                       'nameserver1': whmcs_server.nameserver1,
                       'nameserver1ip': whmcs_server.nameserver1ip,
                       'nameserver2': whmcs_server.nameserver2,
                       'nameserver2ip': whmcs_server.nameserver2ip,
                       'nameserver3': whmcs_server.nameserver3,
                       'nameserver3ip': whmcs_server.nameserver3ip,
                       'nameserver4': whmcs_server.nameserver4,
                       'nameserver4ip': whmcs_server.nameserver4ip,
                       'nameserver5': whmcs_server.nameserver5,
                       'nameserver5ip': whmcs_server.nameserver5ip,
                       'maxaccounts': whmcs_server.maxaccounts,
                       'secure': True if whmcs_server.secure == 'on' else False,
                       'port': whmcs_server.port,
                       'id': whmcs_server.id}
    if whmcs_server.type == 'cpanel':
        server_settings['key'] = fernet_encrypt(whmcs_server.accesshash)
    if whmcs_server.type == 'hypanel':
        server_settings['url'] = whmcs_server.hostname
        server_settings['password'] = fernet_encrypt(whmcs_server.password)
    return server_settings
