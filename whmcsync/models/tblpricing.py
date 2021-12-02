from django.db import models


class Tblpricing(models.Model):
    type = models.CharField(max_length=14)
    currency = models.IntegerField()
    relid = models.IntegerField()
    msetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    qsetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    ssetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    asetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    bsetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    tsetupfee = models.DecimalField(max_digits=16, decimal_places=2)
    monthly = models.DecimalField(max_digits=16, decimal_places=2)
    quarterly = models.DecimalField(max_digits=16, decimal_places=2)
    semiannually = models.DecimalField(max_digits=16, decimal_places=2)
    annually = models.DecimalField(max_digits=16, decimal_places=2)
    biennially = models.DecimalField(max_digits=16, decimal_places=2)
    triennially = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblpricing'
