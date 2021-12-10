from django.db import models


class Tblticketnotes(models.Model):
    ticketid = models.IntegerField()
    admin = models.TextField()
    date = models.DateTimeField()
    message = models.TextField()
    attachments = models.TextField()
    attachments_removed = models.IntegerField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tblticketnotes'
