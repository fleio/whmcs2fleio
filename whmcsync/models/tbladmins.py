from django.db import models


class Tbladmins(models.Model):
    uuid = models.CharField(max_length=255)
    roleid = models.IntegerField()
    username = models.TextField()
    password = models.CharField(max_length=255)
    passwordhash = models.CharField(max_length=255)
    authmodule = models.TextField()
    authdata = models.TextField()
    firstname = models.TextField()
    lastname = models.TextField()
    email = models.TextField()
    signature = models.TextField()
    notes = models.TextField()
    template = models.TextField()
    language = models.TextField()
    disabled = models.IntegerField()
    loginattempts = models.IntegerField()
    supportdepts = models.TextField()
    ticketnotifications = models.TextField()
    homewidgets = models.TextField()
    password_reset_key = models.CharField(max_length=255)
    password_reset_data = models.TextField()
    password_reset_expiry = models.DateTimeField()
    hidden_widgets = models.TextField()
    widget_order = models.TextField()
    user_preferences = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbladmins'
