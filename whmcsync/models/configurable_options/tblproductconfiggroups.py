from django.db import models


class Tblproductconfiggroups(models.Model):
    name = models.TextField()
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblproductconfiggroups'
