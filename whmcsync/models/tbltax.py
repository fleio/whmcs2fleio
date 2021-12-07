from django.db import models


class Tbltax(models.Model):
    level = models.IntegerField()
    name = models.TextField()
    state = models.TextField()
    country = models.TextField()
    taxrate = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'tbltax'
