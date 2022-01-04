from django.db import models


class Tblproductconfiglinks(models.Model):
    gid = models.IntegerField()
    pid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfiglinks'
