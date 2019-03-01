from django.contrib.auth import get_user_model

from whmcsync.whmcsync.utils import PasswordTypes
from .models import SyncedAccount


class WhmcSyncAuthBackend:
    @staticmethod
    def authenticate(request, username=None, password=None):
        try:
            synced_client = SyncedAccount.objects.get(user__username=username)
        except SyncedAccount.DoesNotExist:
            return None
        else:
            if (not synced_client.password_synced and
                    PasswordTypes.password_match(password=password, stored_password=synced_client.user.password)):
                synced_client.user.set_password(password)
                synced_client.user.save()
                synced_client.password_synced = True
                synced_client.save(update_fields=['password_synced'])
                return synced_client.user
            else:
                return None

    def get_user(self, user_id):
        user = get_user_model()
        return user.objects.get(id=user_id)
