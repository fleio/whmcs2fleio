from django.db import models


class Tblservers(models.Model):
    name = models.TextField()
    ipaddress = models.TextField()
    assignedips = models.TextField()
    hostname = models.TextField()
    monthlycost = models.DecimalField(max_digits=16, decimal_places=2)
    noc = models.TextField()
    statusaddress = models.TextField()
    nameserver1 = models.TextField()
    nameserver1ip = models.TextField()
    nameserver2 = models.TextField()
    nameserver2ip = models.TextField()
    nameserver3 = models.TextField()
    nameserver3ip = models.TextField()
    nameserver4 = models.TextField()
    nameserver4ip = models.TextField()
    nameserver5 = models.TextField()
    nameserver5ip = models.TextField()
    maxaccounts = models.IntegerField()
    type = models.TextField()
    username = models.TextField()
    password = models.TextField()
    accesshash = models.TextField()
    secure = models.TextField()
    port = models.IntegerField(blank=True, null=True)
    active = models.IntegerField()
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblservers'
