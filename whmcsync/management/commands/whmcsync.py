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
        parser.add_argument('--ticket-departments',
                            action='store_true',
                            dest='ticketdepartments',
                            default=False,
                            help='Sync ticket plugin departments.')
        parser.add_argument('--all-tickets',
                            action='store_true',
                            dest='alltickets',
                            default=False,
                            help='Sync ticket departments & all tickets.')
        parser.add_argument('-t', '--tickets',
                            nargs='+',
                            metavar='whmcs_ticket_id',
                            help='Sync ticket departments & certain tickets')
        parser.add_argument('--ticket-predefined-replies',
                            action='store_true',
                            dest='ticketpredefinedreplies',
                            default=False,
                            help='Sync ticket predefined replies & related categories.')
        parser.add_argument('--log-level',
                            nargs='?',
                            choices=['WARNING', 'INFO', 'DEBUG', 'ERROR', 'CRITICAL'],
                            help='Set log level. Defaults to WARNING.')
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

    def _sync_services(self, options):
        services_list, exception_list = sync_services(fail_fast=options.get('failfast', False))
        self.stdout.write('\nNumber of synced services: %d \nNumber of services failed to sync: %s'
                          % (len(services_list), len(exception_list)))

    def _sync_product_groups(self, options):
        product_groups_list, exception_list = sync_product_groups(fail_fast=options.get('failfast', False))
        self.stdout.write('\nNumber of synced product groups: %d \nNumber of product groups failed to sync: %s'
                          % (len(product_groups_list), len(exception_list)))

    def _sync_users(self, fail_fast=False, related_to_clients=None):
        users_list, exception_list = sync_users(
            fail_fast=fail_fast,
            related_to_clients=related_to_clients,
        )
        self.stdout.write('\nNumber of synced users: %d \nNumber of users failed to sync: %s'
                          % (len(users_list), len(exception_list)))

    def _sync_staff_users(self, fail_fast=False):
        users_list, exception_list = sync_staff_users(fail_fast=fail_fast,)
        self.stdout.write('\nNumber of synced staff users: %d \nNumber of staff users failed to sync: %s'
                          % (len(users_list), len(exception_list)))

    def _sync_products(self, options):
        products_list, exception_list = sync_products(fail_fast=options.get('failfast', False))
        self.stdout.write('\nNumber of synced products: %d \nNumber of products failed to sync: %s'
                          % (len(products_list), len(exception_list)))

    def _sync_tax_rules(self, options):
        taxes_list, exception_list, skipped_list = sync_tax_rules(fail_fast=options.get('failfast', False))
        self.stdout.write(
            '\nNumber of synced tax rules: %d '
            '\nNumber of tax rules failed to sync: %s '
            '\nNumber of tax rules skipped: %d'
            % (len(taxes_list), len(exception_list), len(skipped_list))
        )

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

    def _sync_ticket_departments(self, fail_fast=False):
        departments_list, exception_list = sync_ticket_departments(fail_fast=fail_fast)
        self.stdout.write('\nNumber of synced departments: %d \nNumber of departments failed to sync: %s'
                          % (len(departments_list), len(exception_list)))

    def _sync_tickets(self, fail_fast=False, whmcs_ids=None):
        tickets_list, exception_list = sync_tickets(fail_fast=fail_fast, whmcs_ids=whmcs_ids)
        self.stdout.write('\nNumber of synced tickets: %d \nNumber of tickets failed to sync: %s'
                          % (len(tickets_list), len(exception_list)))

    def _sync_ticket_predefined_reply_categories(self, options):
        categories_list, exception_list = sync_predefined_reply_categories(fail_fast=options.get('failfast', False))
        self.stdout.write(
            '\nNumber of synced ticket predefined reply categories: %d '
            '\nNumber of ticket predefined reply categories failed to sync: %s'
            % (len(categories_list), len(exception_list))
        )

    def _sync_ticket_predefined_replies(self, options):
        replies_list, exception_list = sync_predefined_replies(fail_fast=options.get('failfast', False))
        self.stdout.write(
            '\nNumber of synced ticket predefined replies: %d '
            '\nNumber of ticket predefined replies failed to sync: %s'
            % (len(replies_list), len(exception_list))
        )

    def handle(self, *args, **options):
        """Execute the sync command and take into account any parameters passed"""
        WHMCS_LOGGER.setLevel(options.get('log_level') or 'WARNING')

        verify_settings(ignore_auth_backend=options.get('ignoreauthbackend'))

        fail_fast = options.get('fail_fast')

        if options.get('all') and options.get('clients'):
            raise CommandError('Specify either "--all" or "--clients" not both')

        if options.get('taxrules'):
            self._sync_tax_rules(options=options)

        if options.get('currencies'):
            sync_currencies(fail_fast=fail_fast, default=False)

        if options.get('users'):
            self._sync_staff_users(fail_fast=fail_fast)
            self._sync_users(fail_fast=fail_fast)

        if options.get('clientgroups'):
            self._sync_client_groups(options=options)

        if options.get('allclients') or options.get('activeonly'):
            self._sync_currencies(options=options)
            self._sync_client_groups(options=options)
            self._sync_users(fail_fast=fail_fast)
            self._sync_clients(options=options)
            sync_user_to_clients(fail_fast=fail_fast)

        clients = options.get('clients')
        if clients:
            self._sync_currencies(options=options)
            self._sync_client_groups(options=options)
            self._sync_users(fail_fast=fail_fast, related_to_clients=clients)  # will sync only for given clients
            self._sync_clients(options=options, whmcs_ids=clients)
            sync_user_to_clients(fail_fast=fail_fast, related_to_clients=clients)

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
            # if trying to sync service without related client/product already synced, it will be skipped with a warning
            self._sync_services(options=options)

        if options.get('ticketdepartments'):
            self._sync_ticket_departments(fail_fast=fail_fast)

        ticket_ids = options.get('tickets')
        if ticket_ids or options.get('alltickets'):
            self._sync_ticket_departments(fail_fast=fail_fast)
            self._sync_tickets(fail_fast=fail_fast, whmcs_ids=ticket_ids)

        if options.get('ticketpredefinedreplies'):
            self._sync_ticket_predefined_reply_categories(options=options)
            self._sync_ticket_predefined_replies(options=options)

