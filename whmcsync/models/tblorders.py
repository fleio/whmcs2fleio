from django.db import models


class Tblorders(models.Model):
    ordernum = models.BigIntegerField()
    userid = models.IntegerField()
    contactid = models.IntegerField()
    requestor_id = models.PositiveIntegerField()
    admin_requestor_id = models.PositiveIntegerField()
    date = models.DateTimeField()
    nameservers = models.TextField()
    transfersecret = models.TextField()
    renewals = models.TextField()
    promocode = models.TextField()
    promotype = models.TextField()
    promovalue = models.TextField()
    orderdata = models.TextField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    paymentmethod = models.TextField()
    invoiceid = models.IntegerField()
    status = models.TextField()
    ipaddress = models.TextField()
    fraudmodule = models.TextField()
    fraudoutput = models.TextField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblorders'