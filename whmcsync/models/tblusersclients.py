from django.db import models


class TblusersClients(models.Model):
    auth_user_id = models.PositiveIntegerField()
    client_id = models.PositiveIntegerField()
    invite_id = models.PositiveIntegerField()
    owner = models.PositiveIntegerField()
    permissions = models.TextField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblusers_clients'
        unique_together = (('auth_user_id', 'client_id'),)
