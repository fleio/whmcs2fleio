from django.db import models


class Tbltickets(models.Model):
    tid = models.CharField(max_length=128, blank=True, null=True)
    did = models.IntegerField()  # related department
    userid = models.IntegerField()  # related client
    contactid = models.IntegerField()
    requestor_id = models.PositiveIntegerField()  # user that created ticket
    name = models.TextField()
    email = models.TextField()
    cc = models.TextField()
    c = models.TextField()
    ipaddress = models.CharField(max_length=64, blank=True, null=True)
    date = models.DateTimeField()
    title = models.TextField()
    message = models.TextField()
    status = models.CharField(max_length=64)
    urgency = models.TextField()
    admin = models.TextField()
    attachment = models.TextField()
    attachments_removed = models.IntegerField()
    lastreply = models.DateTimeField()
    flag = models.IntegerField()  # assigned admin
    clientunread = models.IntegerField()
    adminunread = models.TextField()
    replyingadmin = models.IntegerField()
    replyingtime = models.DateTimeField()
    service = models.TextField()
    merged_ticket_id = models.IntegerField()
    editor = models.CharField(max_length=8)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltickets'
