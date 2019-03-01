from django.db import models


class Tblcontacts(models.Model):
    userid = models.IntegerField()
    firstname = models.TextField()
    lastname = models.TextField()
    companyname = models.TextField()
    email = models.TextField()
    address1 = models.TextField()
    address2 = models.TextField()
    city = models.TextField()
    state = models.TextField()
    postcode = models.TextField()
    country = models.TextField()
    phonenumber = models.TextField()
    subaccount = models.IntegerField()
    password = models.TextField()
    permissions = models.TextField()
    domainemails = models.IntegerField()
    generalemails = models.IntegerField()
    invoiceemails = models.IntegerField()
    productemails = models.IntegerField()
    supportemails = models.IntegerField()
    affiliateemails = models.IntegerField()
    pwresetkey = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pwresetexpiry = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblcontacts'

