from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from whmcsync.whmcsync.exceptions import DBSyncException
from whmcsync.whmcsync.sync.clients import sync_all_clients
from whmcsync.whmcsync.sync.clients import sync_client
from whmcsync.whmcsync.operations import verify_settings
from whmcsync.whmcsync.sync.client_groups import sync_client_groups
from whmcsync.whmcsync.sync.currencies import sync_currencies
from whmcsync.whmcsync.sync.product_groups import sync_product_groups
from whmcsync.whmcsync.sync.products import sync_products
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
        parser.add_argument('--all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help='Sync all clients from WHMCS')
        parser.add_argument('--active-only',
                            action='store_true',
                            dest='activeonly',
                            default=False,
                            help='Sync only active clients.')
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

    def handle(self, *args, **options):
        """Execute the sync command and take into account any parameters passed"""

        verify_settings(ignore_auth_backend=options.get('ignoreauthbackend'))

        if options.get('all') and options.get('clients'):
            raise CommandError('Specify either "--all" or "--clients" not both')
        # TODO: remove the line below
        self.stdout.write('{} {}'.format(args, options))

        if options.get('taxes'):
            sync_tax_rules(fail_fast=options.get('failfast'))

        if options.get('currencies'):
            # NOTE: sync all currencies first in order to have them for clients
            # default will sync the rates and the default currency too
            sync_currencies(fail_fast=options.get('failfast'), default=False)

        if options.get('all'):
            sync_client_groups(options=options)  # NOTE(tomo): Sync client groups first
            client_list, exception_list = sync_all_clients(fail_fast=options.get('failfast', False))
            for exception in exception_list:
                self.stderr.write('{}'.format(exception))
            if client_list:
                self.stdout.write('Successfully synced WHMCS client(s):')
                for client_display in client_list:
                    self.stdout.write(str(client_display), ending='\n')
            self.stdout.write('\nNumber of synced clients: %d \nNumber of clients failed to sync: %s'
                              % (len(client_list), len(exception_list)))

        if options.get('clients'):
            client_list = options.get('clients')
            for whmcs_id in client_list:
                try:
                    self.stdout.write('Successfully synced WHMCS client %s' % sync_client(whmcs_id))
                except DBSyncException as ex:
                    self.stderr.write('{}'.format(ex))
                    if options.get('failfast'):
                        break

        if options.get('products'):
            failfast = options.get('failfast', False)
            sync_servers(options)
            group_list, exception_list = sync_product_groups(fail_fast=failfast)
            for gname in group_list:
                self.stdout.write('Successfully synced WHMCS product group: {}'.format(gname))
            if len(exception_list):
                self.stdout.write('The following exceptions occured: \n')
            for exe in exception_list:
                self.stdout.write(str(exe))
            prod_list, exception_list = sync_products(fail_fast=failfast)
            for prod in prod_list:
                self.stdout.write('Product synced: {}'.format(prod))
            if len(exception_list):
                self.stdout.write('The following product sync exceptions occured: \n')
                for exe in exception_list:
                    self.stdout.write(str(exe))
        if options.get('services'):
            service_list, exception_list = sync_services(fail_fast=options.get('failfast', False))
            if exception_list and len(exception_list):
                for exe in exception_list:
                    self.stdout.write(str(exe))
