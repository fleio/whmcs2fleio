from whmcsync.whmcsync.models import SyncedAccount


class WhmcSyncRouter:
    @staticmethod
    def db_for_read(model, **hints):
        if model._meta.app_label == 'whmcsync' and model != SyncedAccount:
            return 'whmcs'
        else:
            return 'default'

    @staticmethod
    def db_for_write(model, **hints):
        if model._meta.app_label == 'whmcsync' and model != SyncedAccount:
            return 'whmcs'
        return 'default'

    @staticmethod
    def allow_migrate(db, app_label, model=None, **hints):
        if 'model_name' in hints and hints['model_name'] == 'syncedaccount' and app_label == 'whmcsync':
            return db == 'default'
        if app_label == 'whmcsync' and model != SyncedAccount:
            return db == 'whmcs'
        else:
            return db == 'default'
