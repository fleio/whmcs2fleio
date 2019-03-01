from django.core.management.base import CommandError


class SettingsNotConfigured(CommandError):
    pass


class DBSyncException(CommandError):
    pass


class DryRunException(CommandError):
    pass
