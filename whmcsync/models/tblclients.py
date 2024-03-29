from django.db import models


class Tblclients(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=255, db_index=True)
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
    tax_id = models.CharField(max_length=128)
    password = models.TextField()
    authmodule = models.TextField()
    authdata = models.TextField()
    currency = models.ForeignKey(to='whmcsync.Tblcurrencies', db_constraint=False, db_column='currency',
                                 on_delete=models.CASCADE)
    defaultgateway = models.TextField()
    credit = models.DecimalField(max_digits=16, decimal_places=2)
    taxexempt = models.IntegerField()
    latefeeoveride = models.IntegerField()
    overideduenotices = models.IntegerField()
    separateinvoices = models.IntegerField()
    disableautocc = models.IntegerField()
    datecreated = models.DateField()
    notes = models.TextField()
    billingcid = models.IntegerField()
    securityqid = models.IntegerField()
    securityqans = models.TextField()
    groupid = models.IntegerField()
    cardtype = models.CharField(max_length=255)
    cardlastfour = models.TextField()
    cardnum = models.TextField()
    startdate = models.TextField()
    expdate = models.TextField()
    issuenumber = models.TextField()
    bankname = models.TextField()
    banktype = models.TextField()
    bankcode = models.TextField()
    bankacct = models.TextField()
    gatewayid = models.TextField()
    lastlogin = models.DateTimeField(blank=True, null=True)
    ip = models.TextField()
    host = models.TextField()
    status = models.CharField(max_length=8)
    language = models.TextField()
    pwresetkey = models.TextField()
    emailoptout = models.IntegerField()
    marketing_emails_opt_in = models.PositiveIntegerField()
    overrideautoclose = models.IntegerField()
    allow_sso = models.IntegerField()
    email_verified = models.IntegerField()
    email_preferences = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pwresetexpiry = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblclients'

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)
