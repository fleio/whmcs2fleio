from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from whmcsync.whmcsync.sync.client_contacts import sync_contacts
from whmcsync.whmcsync.sync.clients import sync_clients
from whmcsync.whmcsync.operations import verify_settings
from whmcsync.whmcsync.sync.client_groups import sync_client_groups
from whmcsync.whmcsync.sync.currencies import sync_currencies
from whmcsync.whmcsync.sync.product_groups import sync_product_groups
from whmcsync.whmcsync.sync.products import sync_products
from whmcsync.whmcsync.sync.servers import sync_server_groups
from whmcsync.whmcsync.sync.servers import sync_servers
from whmcsync.whmcsync.sync.services import sync_services
from whmcsync.whmcsync.sync.tax_rules import sync_tax_rules


class Command(BaseCommand):
    help = 'Sync one or more clients from WHMCS including associated resources and settings'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--clients',
                            nargs='+',
                            metavar='whmcs_client_id',
                            help='Sync only specified clients')
        parser.add_argument('--all-clients',
                            action='store_true',
                            dest='allclients',
                            default=False,
                            help='Sync all clients from WHMCS')
        parser.add_argument('--contacts',
                            action='store_true',
                            dest='contacts',
                            default=False,
                            help='Sync all contacts from WHMCS for synced Fleio clients')
        parser.add_argument('--active-only',
                            action='store_true',
                            dest='activeonly',
                            default=False,
                            help='Sync only active clients.')
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
        parser.add_argument('--ignore-auth-backend',
                            action='store_true',
                            dest='ignoreauthbackend',
                            default=False,
                            help=('Skip authentication backend settings check. '
                                  'The authentication backend module is used to allow WHMCS users to login with '
                                  'their old username and password'))
        parser.add_argument('--taxes',
                            action='store_true',
                            dest='taxrules',
                            default=False,
                            help='Sync tax rules.')
        parser.add_argument('--currencies',
                            action='store_true',
                            dest='currencies',
                            default=False,
                            help='Sync currencies with existing rates.')
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dryrun',
                            default=False,
                            help='Do not modify any data. Only print what will be changed')

    def _sync_client_groups(self, options):
        groups_list, exception_list = sync_client_groups(options=options)
        self.stdout.write('\nNumber of synced client groups: %d \nNumber of client groups failed to sync: %s'
                          % (len(groups_list), len(exception_list)))

    def _sync_currencies(self, options):
        currencies_list, exception_list = sync_currencies(fail_fast=options.get('failfast'), default=False)
        self.stdout.write('\nNumber of synced currencies: %d \nNumber of currencies failed to sync: %s'
                          % (len(currencies_list), len(exception_list)))

    def _sync_server_groups(self, options):
        groups_list, exception_list = sync_server_groups(options=options)
        self.stdout.write('\nNumber of synced server groups: %d \nNumber of server groups failed to sync: %s'
                          % (len(groups_list), len(exception_list)))

    def _sync_servers(self, options):
        servers_list, exception_list = sync_servers(options=options)
        self.stdout.write('\nNumber of synced servers: %d \nNumber of servers failed to sync: %s'
                          % (len(servers_list), len(exception_list)))

    def _sync_product_groups(self, options):
        product_groups_list, exception_list = sync_product_groups(fail_fast=options.get('failfast', False))
        self.stdout.write('\nNumber of synced product groups: %d \nNumber of product groups failed to sync: %s'
                          % (len(product_groups_list), len(exception_list)))

    def _sync_products(self, options):
        products_list, exception_list = sync_products(fail_fast=options.get('failfast', False))
        self.stdout.write('\nNumber of synced products: %d \nNumber of products failed to sync: %s'
                          % (len(products_list), len(exception_list)))

    def _sync_contacts(self, options):
        client_contacts_list, exception_list = sync_contacts(fail_fast=options.get('failfast'))
        if client_contacts_list:
            self.stdout.write('\nSuccessfully synced WHMCS contacts for client(s):\n')
            for client_contacts_display in client_contacts_list:
                self.stdout.write(str(client_contacts_display), ending='\n')

    def _sync_clients(self, options, whmcs_ids=None):
        client_list, exception_list = sync_clients(
            fail_fast=options.get('failfast', False),
            whmcs_ids=whmcs_ids,
            active_only=options.get('activeonly', False),
        )
        if client_list:
            self.stdout.write('\nSuccessfully synced WHMCS client(s):\n')
            for client_display in client_list:
                self.stdout.write(str(client_display), ending='\n')
        self.stdout.write('\nNumber of synced clients: %d \nNumber of clients failed to sync: %s'
                          % (len(client_list), len(exception_list)))

    def handle(self, *args, **options):
        """Execute the sync command and take into account any parameters passed"""

        verify_settings(ignore_auth_backend=options.get('ignoreauthbackend'))

        if options.get('all') and options.get('clients'):
            raise CommandError('Specify either "--all" or "--clients" not both')

        if options.get('taxes'):
            sync_tax_rules(fail_fast=options.get('failfast'))

        if options.get('currencies'):
            sync_currencies(fail_fast=options.get('failfast'), default=False)

        if options.get('clientgroups'):
            self._sync_client_groups(options=options)

        if options.get('allclients') or options.get('activeonly'):
            self._sync_currencies(options=options)
            self._sync_client_groups(options=options)
            self._sync_clients(options=options)

        if options.get('clients'):
            self._sync_currencies(options=options)
            self._sync_client_groups(options=options)
            self._sync_clients(options=options, whmcs_ids=options.get('clients'))

        if options.get('contacts'):
            self._sync_contacts(options=options)

        if options.get('servergroups'):
            self._sync_server_groups(options)

        if options.get('servers'):
            self._sync_server_groups(options)
            self._sync_servers(options)

        if options.get('productgroups'):
            self._sync_product_groups(options=options)

        if options.get('products'):
            self._sync_product_groups(options=options)
            self._sync_server_groups(options=options)  # sync server groups for module settings (e.g. cpanel server)
            self._sync_currencies(options=options)
            self._sync_products(options=options)

        if options.get('services'):
            service_list, exception_list = sync_services(fail_fast=options.get('failfast', False))
            if exception_list and len(exception_list):
                for exe in exception_list:
                    self.stdout.write(str(exe))
