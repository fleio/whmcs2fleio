from django.db import models


class Tblproductgroups(models.Model):
    name = models.TextField()
    headline = models.TextField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)
    orderfrmtpl = models.TextField()
    disabledgateways = models.TextField()
    hidden = models.IntegerField()
    order = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproductgroups'
