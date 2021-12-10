from django.db import models


class Tblticketdepartments(models.Model):
    name = models.TextField()
    description = models.TextField()
    email = models.TextField()
    clientsonly = models.TextField()
    piperepliesonly = models.TextField()
    noautoresponder = models.TextField()
    hidden = models.TextField()
    order = models.IntegerField()
    host = models.TextField()
    port = models.TextField()
    login = models.TextField()
    password = models.TextField()
    mail_auth_config = models.TextField(blank=True, null=True)
    feedback_request = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblticketdepartments'