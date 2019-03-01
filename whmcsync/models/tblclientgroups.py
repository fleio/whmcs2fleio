from django.db import models


class Tblclientgroups(models.Model):
    groupname = models.CharField(max_length=45)
    groupcolour = models.CharField(max_length=45, blank=True, null=True)
    discountpercent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    susptermexempt = models.TextField(blank=True, null=True)
    separateinvoices = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblclientgroups'
