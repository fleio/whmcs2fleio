from django.db import models


class Tblticketpredefinedreplies(models.Model):
    catid = models.IntegerField()
    name = models.TextField()
    reply = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketpredefinedreplies'
