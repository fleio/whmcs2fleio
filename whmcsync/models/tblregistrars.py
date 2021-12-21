from django.db import models


class Tblregistrars(models.Model):
    registrar = models.TextField()
    setting = models.TextField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblregistrars'
