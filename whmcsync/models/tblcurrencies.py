from django.db import models


class Tblcurrencies(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    prefix = models.TextField()
    suffix = models.TextField()
    format = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=5)
    default = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblcurrencies'


