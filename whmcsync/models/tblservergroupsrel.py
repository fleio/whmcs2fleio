from django.db import models


class Tblservergroupsrel(models.Model):
    groupid = models.IntegerField()
    serverid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'tblservergroupsrel'
