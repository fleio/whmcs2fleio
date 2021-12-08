from django.db import models

from fleio.core.models import Client
from fleio.core.models import AppUser


class SyncedAccount(models.Model):
    """Stores clients and users that were synced from WHMCS."""
    whmcs_id = models.IntegerField()
    whmcs_uuid = models.CharField(max_length=64, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.CASCADE)
    subaccount = models.BooleanField(default=False, db_index=True)
    password_synced = models.BooleanField(default=False)

    def __str__(self):
        return self.client.email
