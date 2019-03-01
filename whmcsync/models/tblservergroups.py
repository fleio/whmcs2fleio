from django.db import models


class Tblservergroups(models.Model):
    name = models.TextField()
    filltype = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblservergroups'
