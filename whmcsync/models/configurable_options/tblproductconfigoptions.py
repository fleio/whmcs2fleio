from django.db import models


class Tblproductconfigoptions(models.Model):
    gid = models.IntegerField()
    optionname = models.TextField()
    optiontype = models.TextField()
    qtyminimum = models.IntegerField()
    qtymaximum = models.IntegerField()
    order = models.IntegerField()
    hidden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfigoptions'
