from django.db import models


class Tblaccounts(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    currency = models.IntegerField()
    gateway = models.TextField()
    date = models.DateTimeField(blank=True, null=True)
    description = models.TextField()
    amountin = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    amountout = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=5)
    transid = models.TextField()
    invoiceid = models.IntegerField()
    refundid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblaccounts'
