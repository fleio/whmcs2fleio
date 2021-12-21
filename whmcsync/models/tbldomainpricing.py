from django.db import models


class Tbldomainpricing(models.Model):
    extension = models.TextField()
    dnsmanagement = models.IntegerField()
    emailforwarding = models.IntegerField()
    idprotection = models.IntegerField()
    eppcode = models.IntegerField()
    autoreg = models.TextField()
    order = models.IntegerField()
    group = models.CharField(max_length=5)
    grace_period = models.IntegerField()
    grace_period_fee = models.DecimalField(max_digits=16, decimal_places=2)
    redemption_grace_period = models.IntegerField()
    redemption_grace_period_fee = models.DecimalField(max_digits=16, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomainpricing'
