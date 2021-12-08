from django.contrib.auth import get_user_model

from whmcsync.whmcsync.utils import PasswordTypes
from .models import SyncedAccount


AppUser = get_user_model()


class WhmcSyncAuthBackend:
    @staticmethod
    def authenticate(request, username=None, password=None):
        synced_account = SyncedAccount.objects.filter(user__username=username).first()
        if synced_account:
            if (not synced_account.password_synced and
                    PasswordTypes.password_match(password=password, stored_password=synced_account.user.password)):
                synced_account.user.set_password(password)
                synced_account.user.save()
                synced_account.password_synced = True
                synced_account.save(update_fields=['password_synced'])
                return synced_account.user
            else:
                return None
        else:
            # SyncedAccount not there yet
            user = AppUser.objects.filter(username=username).first()
            if not user:
                return None
            if PasswordTypes.password_match(password=password, stored_password=user.password):
                user.set_password(password)
                return user
            else:
                return None

    def get_user(self, user_id):
        return AppUser.objects.get(id=user_id)
