from django.db import models


class Tblticketpredefinedcats(models.Model):
    parentid = models.IntegerField()
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketpredefinedcats'
