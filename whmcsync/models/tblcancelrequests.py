from django.db import models


class Tblcancelrequests(models.Model):
    date = models.DateTimeField()
    relid = models.IntegerField()
    reason = models.TextField()
    type = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblcancelrequests'
