from django.db import models


class Tblhosting(models.Model):
    userid = models.IntegerField()
    orderid = models.IntegerField()
    packageid = models.IntegerField()
    server = models.IntegerField()
    regdate = models.DateField()
    domain = models.TextField()
    paymentmethod = models.TextField()
    qty = models.PositiveIntegerField()
    firstpaymentamount = models.DecimalField(max_digits=16, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    billingcycle = models.TextField()
    nextduedate = models.DateField(blank=True, null=True)
    nextinvoicedate = models.DateField()
    termination_date = models.DateField()
    completed_date = models.DateField()
    domainstatus = models.CharField(max_length=10)
    username = models.TextField()
    password = models.TextField()
    notes = models.TextField()
    subscriptionid = models.TextField()
    promoid = models.IntegerField()
    promocount = models.IntegerField(blank=True, null=True)
    suspendreason = models.TextField()
    overideautosuspend = models.IntegerField()
    overidesuspenduntil = models.DateField()
    dedicatedip = models.TextField()
    assignedips = models.TextField()
    ns1 = models.TextField()
    ns2 = models.TextField()
    diskusage = models.IntegerField()
    disklimit = models.IntegerField()
    bwusage = models.IntegerField()
    bwlimit = models.IntegerField()
    lastupdate = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblhosting'
