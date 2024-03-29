from django.db import models


class Tblproducts(models.Model):
    type = models.TextField()
    gid = models.IntegerField()
    name = models.TextField()
    slug = models.CharField(max_length=128)
    description = models.TextField()
    hidden = models.IntegerField()
    showdomainoptions = models.IntegerField()
    welcomeemail = models.IntegerField()
    stockcontrol = models.IntegerField()
    qty = models.IntegerField()
    proratabilling = models.IntegerField()
    proratadate = models.IntegerField()
    proratachargenextmonth = models.IntegerField()
    paytype = models.TextField()
    allowqty = models.IntegerField()
    subdomain = models.TextField()
    autosetup = models.TextField()
    servertype = models.TextField()
    servergroup = models.IntegerField()
    configoption1 = models.TextField()
    configoption2 = models.TextField()
    configoption3 = models.TextField()
    configoption4 = models.TextField()
    configoption5 = models.TextField()
    configoption6 = models.TextField()
    configoption7 = models.TextField()
    configoption8 = models.TextField()
    configoption9 = models.TextField()
    configoption10 = models.TextField()
    configoption11 = models.TextField()
    configoption12 = models.TextField()
    configoption13 = models.TextField()
    configoption14 = models.TextField()
    configoption15 = models.TextField()
    configoption16 = models.TextField()
    configoption17 = models.TextField()
    configoption18 = models.TextField()
    configoption19 = models.TextField()
    configoption20 = models.TextField()
    configoption21 = models.TextField()
    configoption22 = models.TextField()
    configoption23 = models.TextField()
    configoption24 = models.TextField()
    freedomain = models.TextField()
    freedomainpaymentterms = models.TextField()
    freedomaintlds = models.TextField()
    recurringcycles = models.IntegerField()
    autoterminatedays = models.IntegerField()
    autoterminateemail = models.IntegerField()
    configoptionsupgrade = models.IntegerField()
    billingcycleupgrade = models.TextField()
    upgradeemail = models.IntegerField()
    overagesenabled = models.CharField(max_length=10)
    overagesdisklimit = models.IntegerField()
    overagesbwlimit = models.IntegerField()
    overagesdiskprice = models.DecimalField(max_digits=6, decimal_places=4)
    overagesbwprice = models.DecimalField(max_digits=6, decimal_places=4)
    tax = models.IntegerField()
    affiliateonetime = models.IntegerField()
    affiliatepaytype = models.TextField()
    affiliatepayamount = models.DecimalField(max_digits=16, decimal_places=2)
    order = models.IntegerField()
    retired = models.IntegerField()
    is_featured = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproducts'
