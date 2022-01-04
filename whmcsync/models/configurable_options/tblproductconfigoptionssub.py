from django.db import models


class Tblproductconfigoptionssub(models.Model):
    configid = models.IntegerField()
    optionname = models.TextField()
    sortorder = models.IntegerField()
    hidden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfigoptionssub'
