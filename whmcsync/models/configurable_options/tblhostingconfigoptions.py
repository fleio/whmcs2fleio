from django.db import models


class Tblhostingconfigoptions(models.Model):
    relid = models.IntegerField()
    configid = models.IntegerField()
    optionid = models.IntegerField()
    qty = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblhostingconfigoptions'
