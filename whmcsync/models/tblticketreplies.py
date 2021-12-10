from django.db import models


class Tblticketreplies(models.Model):
    tid = models.IntegerField()
    userid = models.IntegerField()
    contactid = models.IntegerField()
    requestor_id = models.PositiveIntegerField()
    name = models.TextField()
    email = models.TextField()
    date = models.DateTimeField()
    message = models.TextField()
    admin = models.TextField()
    attachment = models.TextField()
    attachments_removed = models.IntegerField()
    rating = models.IntegerField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tblticketreplies'
