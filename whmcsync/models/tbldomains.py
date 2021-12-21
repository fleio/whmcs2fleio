from django.db import models


class Tbldomains(models.Model):
    userid = models.IntegerField()
    orderid = models.IntegerField()
    type = models.CharField(max_length=8)
    registrationdate = models.DateField()
    domain = models.TextField()
    firstpaymentamount = models.DecimalField(max_digits=16, decimal_places=2)
    recurringamount = models.DecimalField(max_digits=16, decimal_places=2)
    registrar = models.TextField()
    registrationperiod = models.IntegerField()
    expirydate = models.DateField(blank=True, null=True)
    subscriptionid = models.TextField()
    promoid = models.IntegerField()
    status = models.CharField(max_length=20)
    nextduedate = models.DateField()
    nextinvoicedate = models.DateField()
    additionalnotes = models.TextField()
    paymentmethod = models.TextField()
    dnsmanagement = models.IntegerField()
    emailforwarding = models.IntegerField()
    idprotection = models.IntegerField()
    is_premium = models.IntegerField(blank=True, null=True)
    donotrenew = models.IntegerField()
    reminders = models.TextField()
    synced = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomains'
