from typing import List
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from whmcsync.whmcsync.sync.client_contacts import sync_contacts
from whmcsync.whmcsync.sync.clients import sync_clients
from whmcsync.whmcsync.operations import verify_settings
from whmcsync.whmcsync.sync.client_groups import sync_client_groups
from whmcsync.whmcsync.sync.configurable_options import sync_configurable_options
from whmcsync.whmcsync.sync.currencies import sync_currencies
from whmcsync.whmcsync.sync.domains.domains import sync_domains
from whmcsync.whmcsync.sync.domains.domains_registrars import sync_domain_registrars
from whmcsync.whmcsync.sync.domains.domains_tlds import sync_tlds
from whmcsync.whmcsync.sync.product_groups import sync_product_groups
from whmcsync.whmcsync.sync.products import sync_products
from whmcsync.whmcsync.sync.servers import sync_server_groups
from whmcsync.whmcsync.sync.servers import sync_servers
from whmcsync.whmcsync.sync.services import sync_services
from whmcsync.whmcsync.sync.staff_users import sync_staff_users
from whmcsync.whmcsync.sync.tax_rules import sync_tax_rules
from whmcsync.whmcsync.sync.ticket_departments import sync_ticket_departments
from whmcsync.whmcsync.sync.ticket_predefined_replies import sync_predefined_replies
from whmcsync.whmcsync.sync.ticket_predefined_reply_categories import sync_predefined_reply_categories
from whmcsync.whmcsync.sync.tickets import sync_tickets
from whmcsync.whmcsync.sync.user_to_clients import sync_user_to_clients
from whmcsync.whmcsync.sync.users import sync_users
from whmcsync.whmcsync.utils import WHMCS_LOGGER


class Command(BaseCommand):
    help = 'Sync one or more clients from WHMCS including associated resources and settings'
    options: dict
    import_clients: bool
    all_client_data: bool
    fail_fast: bool
    clients: Optional[List[str]]
    all_clients: bool
    all_configs: bool

    def add_arguments(self, parser):
        parser.add_argument('--all-configs',
                            action='store_true',
                            dest='allconfigs',
                            default=False,
                            help='Imports products & product groups, configurable options, tax rules, '
                                 'ticket predefined replies, domains TLDs pricing & registrars, etc. '
                                 'You can run this before importing clients & related data to ensure you have '
                                 'everything is needed first.')
        parser.add_argument('-c', '--clients',
                            nargs='+',
                            metavar='whmcs_client_id',
                            help='Sync only specified clients')
        parser.add_argument('--all-clients',
                            action='store_true',
                            dest='allclients',
                            default=False,
                            help='Sync all clients from WHMCS')
        parser.add_argument('--all-client-data',
                            action='store_true',
                            dest='allclientdata',
                            default=False,
                            help='Works with --clients and --all-clients. '
                                 'Sync all related client data (services, tickets, ...)')
        parser.add_argument('--contacts',
                            action='store_true',
                            dest='contacts',
                            default=False,
                            help='Sync all contacts from WHMCS for synced Fleio clients')
        parser.add_argument('--client-groups',
                            action='store_true',
                            dest='clientgroups',
                            default=False,
                            help='Sync all client groups from WHMCS')
        parser.add_argument('--server-groups',
                            action='store_true',
                            dest='servergroups',
                            default=False,
                            help='Sync all server groups from WHMCS')
        parser.add_argument('--servers',
                            action='store_true',
                            dest='servers',
                            default=False,
                            help='Sync all servers and server groups from WHMCS')
        parser.add_argument('--product-groups',
                            action='store_true',
                            dest='productgroups',
                            default=False,
                            help='Sync all product groups from WHMCS')
        parser.add_argument('--products',
                            action='store_true',
                            dest='products',
                            default=False,
                            help='Sync all products and product groups from WHMCS')
        parser.add_argument('--configurable-options',
                            action='store_true',
                            dest='configurableoptions',
                            default=False,
                            help='Sync all configurable options from WHMCS')
        parser.add_argument('--services',
                            action='store_true',
                            dest='services',
                            default=False,
                            help='Sync all client services from WHMCS')
        parser.add_argument('--failfast',
                            action='store_true',
                            dest='failfast',
                            default=False,
                            help='Stop syncing at first error.')
        parser.add_argument('--tax-rules',
                            action='store_true',
                            dest='taxrules',
                            default=False,
                            help='Sync tax rules.')
        parser.add_argument('--currencies',
                            action='store_true',
                            dest='currencies',
                            default=False,
                            help='Sync currencies with existing rates.')
        parser.add_argument('--users',
                            action='store_true',
                            dest='users',
                            default=False,
                            help='Sync users.')
        parser.add_argument('--staff-users',
                            action='store_true',
                            dest='staffusers',
                            default=False,
                            help='Sync staff users.')
        parser.add_argument('--ticket-departments',
                            action='store_true',
                            dest='ticketdepartments',
                            default=False,
                            help='Sync ticket plugin departments.')
        parser.add_argument('--all-tickets',
                            action='store_true',
                            dest='alltickets',
                            default=False,
                            help='Sync all tickets.')
        parser.add_argument('-t', '--tickets',
                            nargs='+',
                            metavar='whmcs_ticket_id',
                            help='Sync certain tickets')
        parser.add_argument('--ticket-predefined-replies',
                            action='store_true',
                            dest='ticketpredefinedreplies',
                            default=False,
                            help='Sync ticket predefined replies & related categories.')
        parser.add_argument('--domains-pricing',
                            action='store_true',
                            dest='domainspricing',
                            default=False,
                            help='Sync TLDs and their pricing.')
        parser.add_argument('--domains-registrars',
                            action='store_true',
                            dest='domainsregistrars',
                            default=False,
                            help='Sync registrars for domains plugin.')
        parser.add_argument('--domains',
                            action='store_true',
                            dest='domains',
                            default=False,
                            help='Sync domains.')
        parser.add_argument('--ignore-auth-backend',
                            action='store_true',
                            dest='ignoreauthbackend',
                            default=False,
                            help=('Skip authentication backend settings check. '
                                  'The authentication backend module is used to allow WHMCS users to login with '
                                  'their old username and password'))
        parser.add_argument('--log-level',
                            nargs='?',
                            choices=['WARNING', 'INFO', 'DEBUG', 'ERROR', 'CRITICAL'],
                            help='Set log level. Defaults to WARNING.')
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dryrun',
                            default=False,
                            help='Do not modify any data. Only print what will be changed')

    def _sync_client_groups(self):
        groups_list, exception_list = sync_client_groups(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced client groups: %d \nNumber of client groups failed to sync: %s'
                          % (len(groups_list), len(exception_list)))

    def _sync_currencies(self):
        currencies_list, exception_list = sync_currencies(fail_fast=self.fail_fast, default=False)
        self.stdout.write('\nNumber of synced currencies: %d \nNumber of currencies failed to sync: %s'
                          % (len(currencies_list), len(exception_list)))

    def _sync_server_groups(self):
        groups_list, exception_list = sync_server_groups(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced server groups: %d \nNumber of server groups failed to sync: %s'
                          % (len(groups_list), len(exception_list)))

    def _sync_servers(self):
        servers_list, exception_list = sync_servers(fail_fast=self.fail_fast, related_clients=self.clients)
        self.stdout.write('\nNumber of synced servers: %d \nNumber of servers failed to sync: %s'
                          % (len(servers_list), len(exception_list)))

    def _sync_services(self):
        services_list, exception_list, skipped_list = sync_services(
            fail_fast=self.fail_fast, related_to_clients=self.clients
        )
        self.stdout.write(
            '\nNumber of synced services: %d \n'
            'Number of services failed to sync: %s\n'
            'Number of skipped services (missing related data): %s'
            % (len(services_list), len(exception_list), len(skipped_list))
        )

    def _sync_product_groups(self):
        product_groups_list, exception_list = sync_product_groups(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced product groups: %d \nNumber of product groups failed to sync: %s'
                          % (len(product_groups_list), len(exception_list)))

    def _sync_users(self):
        users_list, exception_list = sync_users(
            fail_fast=self.fail_fast,
            related_to_clients=self.clients,
            with_clients=self.all_clients,
        )
        self.stdout.write('\nNumber of synced users: %d \nNumber of users failed to sync: %s'
                          % (len(users_list), len(exception_list)))

    def _sync_staff_users(self):
        users_list, exception_list = sync_staff_users(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced staff users: %d \nNumber of staff users failed to sync: %s'
                          % (len(users_list), len(exception_list)))

    def _sync_products(self):
        products_list, exception_list = sync_products(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced products: %d \nNumber of products failed to sync: %s'
                          % (len(products_list), len(exception_list)))

    def _sync_configurable_options(self):
        conf_options_list, exception_list = sync_configurable_options(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced conf. options: %d \nNumber of conf. options failed to sync: %s'
                          % (len(conf_options_list), len(exception_list)))

    def _sync_tax_rules(self):
        taxes_list, exception_list, skipped_list = sync_tax_rules(fail_fast=self.fail_fast)
        self.stdout.write(
            '\nNumber of synced tax rules: %d '
            '\nNumber of tax rules failed to sync: %s '
            '\nNumber of tax rules skipped: %d'
            % (len(taxes_list), len(exception_list), len(skipped_list))
        )

    def _sync_contacts(self):
        if self.skip_domains_if_needed():
            return
        client_contacts_list, exception_list = sync_contacts(
            fail_fast=self.fail_fast,
            related_to_clients=self.clients
        )
        if client_contacts_list:
            self.stdout.write(
                '\nSuccessfully synced WHMCS contacts for {} client(s)'
                '\nFailed to sync WHMCS contacts for {} client(s)\n'.format(
                    len(client_contacts_list), len(exception_list),
                ),
            )
            for client_contacts_display in client_contacts_list:
                WHMCS_LOGGER.debug(str(client_contacts_display))

    def _sync_tlds(self):
        if self.skip_domains_if_needed():
            return
        tlds_list, exception_list = sync_tlds(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced TLDs: %d \nNumber of TLDs failed to sync: %s'
                          % (len(tlds_list), len(exception_list)))

    def _sync_registrars(self):
        if self.skip_domains_if_needed():
            return
        registrars_list, exception_list = sync_domain_registrars(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced registrars: %d \nNumber of registrars failed to sync: %s'
                          % (len(registrars_list), len(exception_list)))

    def _sync_domains(self):
        if self.skip_domains_if_needed():
            return
        domains_list, exception_list = sync_domains(fail_fast=self.fail_fast, related_to_clients=self.clients)
        self.stdout.write('\nNumber of synced domains: %d \nNumber of domains failed to sync: %s'
                          % (len(domains_list), len(exception_list)))

    def _sync_clients(self):
        client_list, exception_list = sync_clients(
            fail_fast=self.fail_fast,
            whmcs_ids=self.clients,
        )
        self.stdout.write('\nNumber of synced clients: %d \nNumber of clients failed to sync: %s'
                          % (len(client_list), len(exception_list)))
        for client_display in client_list:
            WHMCS_LOGGER.debug(str(client_display))

        sync_user_to_clients(fail_fast=self.fail_fast)

    def _sync_ticket_departments(self):
        if self.skip_tickets_if_needed():
            return
        departments_list, exception_list = sync_ticket_departments(fail_fast=self.fail_fast)
        self.stdout.write('\nNumber of synced departments: %d \nNumber of departments failed to sync: %s'
                          % (len(departments_list), len(exception_list)))

    def _sync_tickets(self):
        if self.skip_tickets_if_needed():
            return
        tickets_list, exception_list = sync_tickets(
            fail_fast=self.fail_fast, whmcs_ids=self.options.get('tickets'), related_clients=self.clients
        )
        self.stdout.write('\nNumber of synced tickets: %d \nNumber of tickets failed to sync: %s'
                          % (len(tickets_list), len(exception_list)))

    def _sync_ticket_predefined_reply_categories(self):
        if self.skip_tickets_if_needed():
            return
        categories_list, exception_list = sync_predefined_reply_categories(fail_fast=self.fail_fast)
        self.stdout.write(
            '\nNumber of synced ticket predefined reply categories: %d '
            '\nNumber of ticket predefined reply categories failed to sync: %s'
            % (len(categories_list), len(exception_list))
        )

    def _sync_ticket_predefined_replies(self):
        if self.skip_tickets_if_needed():
            return
        replies_list, exception_list = sync_predefined_replies(fail_fast=self.fail_fast)
        self.stdout.write(
            '\nNumber of synced ticket predefined replies: %d '
            '\nNumber of ticket predefined replies failed to sync: %s'
            % (len(replies_list), len(exception_list))
        )

    @staticmethod
    def skip_domains_if_needed():
        skip = 'plugins.domains' not in settings.INSTALLED_APPS
        if skip:
            WHMCS_LOGGER.warning('Skipping domains related import because plugin is missing in INSTALLED_APPS')
        return skip

    @staticmethod
    def skip_tickets_if_needed():
        skip = 'plugins.tickets' not in settings.INSTALLED_APPS
        if skip:
            WHMCS_LOGGER.warning('Skipping tickets related import because plugin is missing in INSTALLED_APPS')
        return skip

    def should_import(self, resource_type, ignore_clients_import=False, is_config=False):
        if is_config and self.all_configs:
            return True
        all_resource_records = 'all{}'.format(resource_type)
        import_resource = self.options.get(resource_type, False) or self.options.get(all_resource_records, False)
        if ignore_clients_import:
            return import_resource
        return import_resource or (self.import_clients and self.all_client_data)

    def handle(self, *args, **options):
        WHMCS_LOGGER.setLevel(options.get('log_level') or 'WARNING')

        verify_settings(ignore_auth_backend=options.get('ignoreauthbackend'))

        self.options = options
        self.fail_fast = self.options.get('fail_fast', False)
        self.all_configs = self.options.get('allconfigs', False)
        self.clients = self.options.get('clients')  # whmcs id list
        self.all_clients = self.options.get('allclients')
        self.all_client_data = self.options.get('allclientdata')
        self.import_clients = bool(self.clients or self.all_clients)

        if self.all_clients and self.clients:
            raise CommandError('Specify either "--all-clients" or "--clients" not both')

        if (self.all_clients or self.clients) is None and self.all_client_data:
            raise CommandError(
                'No clients specified. Use --all-clients or --clients x,y,z along with --all-client-data flag.'
            )

        # Settings and other configs
        if self.should_import(resource_type='currencies', ignore_clients_import=True, is_config=True):
            self._sync_currencies()

        if self.should_import(resource_type='taxrules', ignore_clients_import=True, is_config=True):
            self._sync_tax_rules()

        import_products = self.should_import(resource_type='products', ignore_clients_import=True, is_config=True)
        if import_products:
            self._sync_product_groups()
            self._sync_server_groups()  # sync server groups for module settings (e.g. cpanel server)
            self._sync_products()

        if not import_products and self.should_import(resource_type='productgroups', ignore_clients_import=True):
            self._sync_product_groups()
        if not import_products and self.should_import(resource_type='servergroups', ignore_clients_import=True):
            self._sync_server_groups()

        if self.should_import(resource_type='configurableoptions', ignore_clients_import=True, is_config=True):
            self._sync_configurable_options()

        if self.should_import(resource_type='clientgroups', ignore_clients_import=True, is_config=True):
            self._sync_client_groups()

        if self.should_import(resource_type='ticketpredefinedreplies', ignore_clients_import=True, is_config=True):
            self._sync_ticket_predefined_reply_categories()
            self._sync_ticket_predefined_replies()

        if self.should_import(resource_type='ticketdepartments', ignore_clients_import=True, is_config=True):
            self._sync_ticket_departments()

        should_import_tlds = self.should_import(
            resource_type='domainspricing', ignore_clients_import=True, is_config=True
        )
        should_import_registrars = self.should_import(
            resource_type='domainsregistrars', ignore_clients_import=True, is_config=True
        )
        if should_import_registrars or should_import_tlds:
            # also import registrars before importing TLDs
            self._sync_registrars()
            if should_import_tlds:
                self._sync_tlds()

        # Client data
        if self.should_import(resource_type='users'):
            self._sync_users()

        if self.import_clients:
            self._sync_clients()

        if self.should_import(resource_type='contacts'):
            self._sync_contacts()

        if self.should_import(resource_type='servers'):
            self._sync_servers()

        if self.should_import(resource_type='services'):
            self._sync_services()

        if self.should_import(resource_type='tickets'):
            self._sync_tickets()

        if self.should_import(resource_type='domains'):
            self._sync_domains()

        # Other options unrelated to clients or configs
        if self.should_import(resource_type='staffusers', ignore_clients_import=True):
            self._sync_staff_users()
