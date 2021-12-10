from django.db import models


class Tblticketmaillog(models.Model):
    date = models.DateTimeField()
    to = models.TextField()
    cc = models.TextField()
    name = models.TextField()
    email = models.TextField()
    subject = models.TextField()
    message = models.TextField()
    status = models.TextField()
    attachment = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketmaillog'
