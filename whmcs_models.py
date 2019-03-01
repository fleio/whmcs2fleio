# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ModInvoicedata(models.Model):
    invoiceid = models.IntegerField()
    clientsdetails = models.TextField()
    customfields = models.TextField()

    class Meta:
        managed = False
        db_table = 'mod_invoicedata'


class ModOnlinenic(models.Model):
    domain = models.CharField(max_length=255)
    lockstatus = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mod_onlinenic'


class Tblaccounts(models.Model):
    userid = models.IntegerField()
    currency = models.IntegerField()
    gateway = models.TextField()
    date = models.DateTimeField(blank=True, null=True)
    description = models.TextField()
    amountin = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    amountout = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=5)
    transid = models.TextField()
    invoiceid = models.IntegerField()
    refundid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblaccounts'


class Tblactivitylog(models.Model):
    date = models.DateTimeField()
    description = models.TextField()
    user = models.TextField()
    userid = models.IntegerField()
    ipaddr = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblactivitylog'


class Tbladdonmodules(models.Model):
    module = models.TextField()
    setting = models.TextField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'tbladdonmodules'


class Tbladdons(models.Model):
    packages = models.TextField()
    name = models.TextField()
    description = models.TextField()
    billingcycle = models.TextField()
    tax = models.IntegerField()
    showorder = models.IntegerField()
    downloads = models.TextField()
    autoactivate = models.TextField()
    suspendproduct = models.IntegerField()
    welcomeemail = models.IntegerField()
    type = models.CharField(max_length=16)
    module = models.CharField(max_length=32)
    server_group_id = models.IntegerField()
    weight = models.IntegerField()
    autolinkby = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbladdons'


class Tbladminlog(models.Model):
    adminusername = models.TextField()
    logintime = models.DateTimeField()
    logouttime = models.DateTimeField()
    ipaddress = models.TextField()
    sessionid = models.TextField()
    lastvisit = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbladminlog'


class Tbladminperms(models.Model):
    roleid = models.IntegerField()
    permid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbladminperms'


class Tbladminroles(models.Model):
    name = models.TextField()
    widgets = models.TextField()
    reports = models.TextField()
    systememails = models.IntegerField()
    accountemails = models.IntegerField()
    supportemails = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbladminroles'


class Tbladmins(models.Model):
    uuid = models.CharField(max_length=255)
    roleid = models.IntegerField()
    username = models.TextField()
    password = models.CharField(max_length=255)
    passwordhash = models.CharField(max_length=255)
    authmodule = models.TextField()
    authdata = models.TextField()
    firstname = models.TextField()
    lastname = models.TextField()
    email = models.TextField()
    signature = models.TextField()
    notes = models.TextField()
    template = models.TextField()
    language = models.TextField()
    disabled = models.IntegerField()
    loginattempts = models.IntegerField()
    supportdepts = models.TextField()
    ticketnotifications = models.TextField()
    homewidgets = models.TextField()
    password_reset_key = models.CharField(max_length=255)
    password_reset_data = models.TextField()
    password_reset_expiry = models.DateTimeField()
    hidden_widgets = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbladmins'


class Tbladminsecurityquestions(models.Model):
    question = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbladminsecurityquestions'


class Tblaffiliates(models.Model):
    id = models.AutoField()
    date = models.DateField(blank=True, null=True)
    clientid = models.IntegerField()
    visitors = models.IntegerField()
    paytype = models.TextField()
    payamount = models.DecimalField(max_digits=10, decimal_places=2)
    onetime = models.IntegerField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    withdrawn = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblaffiliates'


class Tblaffiliatesaccounts(models.Model):
    affiliateid = models.IntegerField()
    relid = models.IntegerField()
    lastpaid = models.DateField()

    class Meta:
        managed = False
        db_table = 'tblaffiliatesaccounts'


class Tblaffiliateshistory(models.Model):
    affiliateid = models.IntegerField()
    date = models.DateField()
    affaccid = models.IntegerField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblaffiliateshistory'


class Tblaffiliatespending(models.Model):
    affaccid = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    clearingdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'tblaffiliatespending'


class Tblaffiliateswithdrawals(models.Model):
    affiliateid = models.IntegerField()
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblaffiliateswithdrawals'


class Tblannouncements(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    title = models.TextField()
    announcement = models.TextField()
    published = models.IntegerField()
    parentid = models.IntegerField()
    language = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblannouncements'


class TblapiRoles(models.Model):
    role = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    permissions = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblapi_roles'


class Tblapilog(models.Model):
    action = models.CharField(max_length=255)
    request = models.TextField()
    response = models.TextField()
    status = models.IntegerField()
    headers = models.TextField()
    level = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblapilog'


class Tblapplinks(models.Model):
    module_type = models.CharField(max_length=20)
    module_name = models.CharField(max_length=50)
    is_enabled = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblapplinks'


class TblapplinksLinks(models.Model):
    applink_id = models.PositiveIntegerField()
    scope = models.CharField(max_length=80)
    display_label = models.CharField(max_length=256)
    is_enabled = models.IntegerField()
    order = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblapplinks_links'


class TblapplinksLog(models.Model):
    applink_id = models.PositiveIntegerField()
    message = models.CharField(max_length=2000)
    level = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblapplinks_log'


class TblauthnAccountLinks(models.Model):
    provider = models.CharField(max_length=32)
    remote_user_id = models.CharField(max_length=255, blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    contact_id = models.IntegerField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblauthn_account_links'
        unique_together = (('provider', 'remote_user_id'),)


class TblauthnConfig(models.Model):
    provider = models.CharField(max_length=64)
    setting = models.CharField(max_length=128)
    value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblauthn_config'
        unique_together = (('provider', 'setting'),)


class Tblbannedemails(models.Model):
    domain = models.TextField()
    count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblbannedemails'


class Tblbannedips(models.Model):
    ip = models.TextField()
    reason = models.TextField()
    expires = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblbannedips'


class Tblbillableitems(models.Model):
    userid = models.IntegerField()
    description = models.TextField()
    hours = models.DecimalField(max_digits=5, decimal_places=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recur = models.IntegerField()
    recurcycle = models.TextField()
    recurfor = models.IntegerField()
    invoiceaction = models.IntegerField()
    duedate = models.DateField()
    invoicecount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblbillableitems'


class Tblbundles(models.Model):
    name = models.TextField()
    validfrom = models.DateField()
    validuntil = models.DateField()
    uses = models.IntegerField()
    maxuses = models.IntegerField()
    itemdata = models.TextField()
    allowpromo = models.IntegerField()
    showgroup = models.IntegerField()
    gid = models.IntegerField()
    description = models.TextField()
    displayprice = models.DecimalField(max_digits=10, decimal_places=2)
    sortorder = models.IntegerField()
    is_featured = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblbundles'


class Tblcalendar(models.Model):
    title = models.TextField()
    desc = models.TextField()
    start = models.IntegerField()
    end = models.IntegerField()
    allday = models.IntegerField()
    adminid = models.IntegerField()
    recurid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblcalendar'


class Tblcancelrequests(models.Model):
    date = models.DateTimeField()
    relid = models.IntegerField()
    reason = models.TextField()
    type = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblcancelrequests'


class Tblclientgroups(models.Model):
    groupname = models.CharField(max_length=45)
    groupcolour = models.CharField(max_length=45, blank=True, null=True)
    discountpercent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    susptermexempt = models.TextField(blank=True, null=True)
    separateinvoices = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblclientgroups'


class Tblclients(models.Model):
    uuid = models.CharField(max_length=255)
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
    password = models.TextField()
    authmodule = models.TextField()
    authdata = models.TextField()
    currency = models.IntegerField()
    defaultgateway = models.TextField()
    credit = models.DecimalField(max_digits=10, decimal_places=2)
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
    overrideautoclose = models.IntegerField()
    allow_sso = models.IntegerField()
    email_verified = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pwresetexpiry = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblclients'


class Tblclientsfiles(models.Model):
    userid = models.IntegerField()
    title = models.TextField()
    filename = models.TextField()
    adminonly = models.IntegerField()
    dateadded = models.DateField()

    class Meta:
        managed = False
        db_table = 'tblclientsfiles'


class Tblconfiguration(models.Model):
    setting = models.TextField()
    value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblconfiguration'


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


class Tblcredit(models.Model):
    clientid = models.IntegerField()
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    relid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblcredit'


class Tblcurrencies(models.Model):
    code = models.TextField()
    prefix = models.TextField()
    suffix = models.TextField()
    format = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=5)
    default = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblcurrencies'


class Tblcustomfields(models.Model):
    type = models.TextField()
    relid = models.IntegerField()
    fieldname = models.TextField()
    fieldtype = models.TextField()
    description = models.TextField()
    fieldoptions = models.TextField()
    regexpr = models.TextField()
    adminonly = models.TextField()
    required = models.TextField()
    showorder = models.TextField()
    showinvoice = models.TextField()
    sortorder = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblcustomfields'


class Tblcustomfieldsvalues(models.Model):
    fieldid = models.IntegerField()
    relid = models.IntegerField()
    value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblcustomfieldsvalues'


class Tbldeviceauth(models.Model):
    identifier = models.CharField(unique=True, max_length=255)
    secret = models.CharField(max_length=255)
    compat_secret = models.CharField(max_length=255)
    user_id = models.IntegerField()
    is_admin = models.IntegerField()
    role_ids = models.TextField()
    description = models.CharField(max_length=255)
    last_access = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbldeviceauth'


class TbldomainLookupConfiguration(models.Model):
    registrar = models.CharField(max_length=32)
    setting = models.CharField(max_length=128)
    value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomain_lookup_configuration'


class Tbldomainpricing(models.Model):
    extension = models.TextField()
    dnsmanagement = models.TextField()
    emailforwarding = models.TextField()
    idprotection = models.TextField()
    eppcode = models.TextField()
    autoreg = models.TextField()
    order = models.IntegerField()
    group = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'tbldomainpricing'


class TbldomainpricingPremium(models.Model):
    to_amount = models.DecimalField(unique=True, max_digits=10, decimal_places=2)
    markup = models.DecimalField(max_digits=8, decimal_places=5)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomainpricing_premium'


class Tbldomainreminders(models.Model):
    domain_id = models.IntegerField()
    date = models.DateField()
    recipients = models.TextField()
    type = models.IntegerField()
    days_before_expiry = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbldomainreminders'


class Tbldomains(models.Model):
    userid = models.IntegerField()
    orderid = models.IntegerField()
    type = models.CharField(max_length=8)
    registrationdate = models.DateField()
    domain = models.TextField()
    firstpaymentamount = models.DecimalField(max_digits=10, decimal_places=2)
    recurringamount = models.DecimalField(max_digits=10, decimal_places=2)
    registrar = models.TextField()
    registrationperiod = models.IntegerField()
    expirydate = models.DateField(blank=True, null=True)
    subscriptionid = models.TextField()
    promoid = models.IntegerField()
    status = models.CharField(max_length=16)
    nextduedate = models.DateField()
    nextinvoicedate = models.DateField()
    additionalnotes = models.TextField()
    paymentmethod = models.TextField()
    dnsmanagement = models.IntegerField()
    emailforwarding = models.IntegerField()
    idprotection = models.IntegerField()
    is_premium = models.IntegerField(blank=True, null=True)
    donotrenew = models.IntegerField()
    reminders = models.TextField()
    synced = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomains'


class TbldomainsExtra(models.Model):
    domain_id = models.IntegerField()
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomains_extra'
        unique_together = (('domain_id', 'name'),)


class Tbldomainsadditionalfields(models.Model):
    domainid = models.IntegerField()
    name = models.TextField()
    value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldomainsadditionalfields'


class Tbldownloadcats(models.Model):
    parentid = models.IntegerField()
    name = models.TextField()
    description = models.TextField()
    hidden = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldownloadcats'


class Tbldownloads(models.Model):
    category = models.IntegerField()
    type = models.TextField()
    title = models.TextField()
    description = models.TextField()
    downloads = models.IntegerField()
    location = models.TextField()
    clientsonly = models.IntegerField()
    hidden = models.IntegerField()
    productdownload = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldownloads'


class TbldynamicTranslations(models.Model):
    related_type = models.CharField(max_length=36)
    related_id = models.PositiveIntegerField()
    language = models.CharField(max_length=16)
    translation = models.TextField()
    input_type = models.CharField(max_length=8)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbldynamic_translations'


class Tblemailmarketer(models.Model):
    name = models.TextField()
    type = models.TextField()
    settings = models.TextField()
    disable = models.IntegerField()
    marketing = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblemailmarketer'


class Tblemails(models.Model):
    userid = models.IntegerField()
    subject = models.TextField()
    message = models.TextField()
    date = models.DateTimeField(blank=True, null=True)
    to = models.TextField(blank=True, null=True)
    cc = models.TextField(blank=True, null=True)
    bcc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblemails'


class Tblemailtemplates(models.Model):
    type = models.TextField()
    name = models.TextField()
    subject = models.TextField()
    message = models.TextField()
    attachments = models.TextField()
    fromname = models.TextField()
    fromemail = models.TextField()
    disabled = models.IntegerField()
    custom = models.IntegerField()
    language = models.TextField()
    copyto = models.TextField()
    blind_copy_to = models.TextField()
    plaintext = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblemailtemplates'


class Tblfraud(models.Model):
    fraud = models.TextField()
    setting = models.TextField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblfraud'


class Tblgatewaylog(models.Model):
    date = models.DateTimeField()
    gateway = models.TextField()
    data = models.TextField()
    result = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblgatewaylog'


class Tblhosting(models.Model):
    userid = models.IntegerField()
    orderid = models.IntegerField()
    packageid = models.IntegerField()
    server = models.IntegerField()
    regdate = models.DateField()
    domain = models.TextField()
    paymentmethod = models.TextField()
    firstpaymentamount = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billingcycle = models.TextField()
    nextduedate = models.DateField(blank=True, null=True)
    nextinvoicedate = models.DateField()
    termination_date = models.DateField()
    completed_date = models.DateField()
    domainstatus = models.CharField(max_length=10)
    username = models.TextField()
    password = models.TextField()
    notes = models.TextField()
    subscriptionid = models.TextField()
    promoid = models.IntegerField()
    suspendreason = models.TextField()
    overideautosuspend = models.IntegerField()
    overidesuspenduntil = models.DateField()
    dedicatedip = models.TextField()
    assignedips = models.TextField()
    ns1 = models.TextField()
    ns2 = models.TextField()
    diskusage = models.IntegerField()
    disklimit = models.IntegerField()
    bwusage = models.IntegerField()
    bwlimit = models.IntegerField()
    lastupdate = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblhosting'


class Tblhostingaddons(models.Model):
    orderid = models.IntegerField()
    hostingid = models.IntegerField()
    addonid = models.IntegerField()
    userid = models.IntegerField()
    server = models.IntegerField()
    name = models.TextField()
    setupfee = models.DecimalField(max_digits=10, decimal_places=2)
    recurring = models.DecimalField(max_digits=10, decimal_places=2)
    billingcycle = models.TextField()
    tax = models.TextField()
    status = models.CharField(max_length=10)
    regdate = models.DateField()
    nextduedate = models.DateField(blank=True, null=True)
    nextinvoicedate = models.DateField()
    termination_date = models.DateField()
    paymentmethod = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblhostingaddons'


class Tblhostingconfigoptions(models.Model):
    relid = models.IntegerField()
    configid = models.IntegerField()
    optionid = models.IntegerField()
    qty = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblhostingconfigoptions'


class Tblinvoiceitems(models.Model):
    invoiceid = models.IntegerField()
    userid = models.IntegerField()
    type = models.CharField(max_length=30)
    relid = models.IntegerField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    taxed = models.IntegerField()
    duedate = models.DateField(blank=True, null=True)
    paymentmethod = models.TextField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblinvoiceitems'


class Tblinvoices(models.Model):
    userid = models.IntegerField()
    invoicenum = models.TextField()
    date = models.DateField(blank=True, null=True)
    duedate = models.DateField(blank=True, null=True)
    datepaid = models.DateTimeField()
    last_capture_attempt = models.DateTimeField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    tax2 = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    taxrate = models.DecimalField(max_digits=10, decimal_places=2)
    taxrate2 = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.TextField()
    paymentmethod = models.TextField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblinvoices'


class TbljobsQueue(models.Model):
    name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    method_name = models.CharField(max_length=255)
    input_parameters = models.TextField()
    available_at = models.DateTimeField()
    digest_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbljobs_queue'


class Tblknowledgebase(models.Model):
    title = models.TextField()
    article = models.TextField()
    views = models.IntegerField()
    useful = models.IntegerField()
    votes = models.IntegerField()
    private = models.TextField()
    order = models.IntegerField()
    parentid = models.IntegerField()
    language = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblknowledgebase'


class Tblknowledgebasecats(models.Model):
    parentid = models.IntegerField()
    name = models.TextField()
    description = models.TextField()
    hidden = models.TextField()
    catid = models.IntegerField()
    language = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblknowledgebasecats'


class Tblknowledgebaselinks(models.Model):
    categoryid = models.IntegerField()
    articleid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblknowledgebaselinks'


class Tblknowledgebasetags(models.Model):
    articleid = models.IntegerField()
    tag = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'tblknowledgebasetags'


class Tbllinks(models.Model):
    name = models.TextField()
    link = models.TextField()
    clicks = models.IntegerField()
    conversions = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbllinks'


class TbllogRegister(models.Model):
    name = models.CharField(max_length=255)
    namespace_id = models.PositiveIntegerField(blank=True, null=True)
    namespace = models.CharField(max_length=255)
    namespace_value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbllog_register'


class TblmarketconnectServices(models.Model):
    name = models.CharField(max_length=30)
    status = models.IntegerField()
    product_ids = models.TextField()
    settings = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblmarketconnect_services'


class TblmoduleConfiguration(models.Model):
    entity_type = models.CharField(max_length=8)
    entity_id = models.PositiveIntegerField()
    setting_name = models.CharField(max_length=16)
    friendly_name = models.CharField(max_length=64)
    value = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblmodule_configuration'
        unique_together = (('entity_type', 'entity_id', 'setting_name'),)


class Tblmodulelog(models.Model):
    date = models.DateTimeField()
    module = models.TextField()
    action = models.TextField()
    request = models.TextField()
    response = models.TextField()
    arrdata = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblmodulelog'


class Tblmodulequeue(models.Model):
    service_type = models.CharField(max_length=20)
    service_id = models.PositiveIntegerField()
    module_name = models.CharField(max_length=64)
    module_action = models.CharField(max_length=64)
    last_attempt = models.DateTimeField()
    last_attempt_error = models.TextField()
    num_retries = models.PositiveSmallIntegerField()
    completed = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblmodulequeue'


class Tblnetworkissues(models.Model):
    title = models.CharField(max_length=45)
    description = models.TextField()
    type = models.CharField(max_length=6)
    affecting = models.CharField(max_length=100, blank=True, null=True)
    server = models.PositiveIntegerField(blank=True, null=True)
    priority = models.CharField(max_length=8)
    startdate = models.DateTimeField()
    enddate = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=13)
    lastupdate = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblnetworkissues'


class Tblnotes(models.Model):
    userid = models.IntegerField()
    adminid = models.IntegerField()
    created = models.DateTimeField()
    modified = models.DateTimeField()
    note = models.TextField()
    sticky = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblnotes'


class Tblnotificationproviders(models.Model):
    name = models.CharField(max_length=255)
    settings = models.TextField()
    active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblnotificationproviders'


class Tblnotificationrules(models.Model):
    description = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    events = models.CharField(max_length=255)
    conditions = models.TextField()
    provider = models.CharField(max_length=255)
    provider_config = models.TextField()
    active = models.IntegerField()
    can_delete = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblnotificationrules'


class TbloauthserverAccessTokenScopes(models.Model):
    access_token_id = models.PositiveIntegerField()
    scope_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_access_token_scopes'


class TbloauthserverAccessTokens(models.Model):
    access_token = models.CharField(unique=True, max_length=80)
    client_id = models.CharField(max_length=80)
    user_id = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=2000)
    expires = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_access_tokens'


class TbloauthserverAuthCodes(models.Model):
    authorization_code = models.CharField(unique=True, max_length=80)
    client_id = models.CharField(max_length=80)
    user_id = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=2000)
    id_token = models.CharField(max_length=2000)
    expires = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_auth_codes'


class TbloauthserverAuthcodeScopes(models.Model):
    authorization_code_id = models.PositiveIntegerField()
    scope_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_authcode_scopes'


class TbloauthserverClientScopes(models.Model):
    client_id = models.PositiveIntegerField()
    scope_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_client_scopes'


class TbloauthserverClients(models.Model):
    identifier = models.CharField(unique=True, max_length=80)
    secret = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=2000)
    grant_types = models.CharField(max_length=80)
    user_id = models.CharField(max_length=255)
    service_id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    logo_uri = models.CharField(max_length=255)
    rsa_key_pair_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_clients'


class TbloauthserverScopes(models.Model):
    scope = models.CharField(unique=True, max_length=80)
    description = models.CharField(max_length=255)
    is_default = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_scopes'


class TbloauthserverUserAuthz(models.Model):
    user_id = models.CharField(max_length=255)
    client_id = models.PositiveIntegerField()
    expires = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_user_authz'


class TbloauthserverUserAuthzScopes(models.Model):
    user_authz_id = models.PositiveIntegerField()
    scope_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'tbloauthserver_user_authz_scopes'


class Tblorders(models.Model):
    ordernum = models.BigIntegerField()
    userid = models.IntegerField()
    contactid = models.IntegerField()
    date = models.DateTimeField()
    nameservers = models.TextField()
    transfersecret = models.TextField()
    renewals = models.TextField()
    promocode = models.TextField()
    promotype = models.TextField()
    promovalue = models.TextField()
    orderdata = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paymentmethod = models.TextField()
    invoiceid = models.IntegerField()
    status = models.TextField()
    ipaddress = models.TextField()
    fraudmodule = models.TextField()
    fraudoutput = models.TextField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblorders'


class Tblorderstatuses(models.Model):
    title = models.TextField()
    color = models.TextField()
    showpending = models.IntegerField()
    showactive = models.IntegerField()
    showcancelled = models.IntegerField()
    sortorder = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblorderstatuses'


class Tblpaymentgateways(models.Model):
    gateway = models.TextField()
    setting = models.TextField()
    value = models.TextField()
    order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblpaymentgateways'


class Tblpricing(models.Model):
    type = models.CharField(max_length=14)
    currency = models.IntegerField()
    relid = models.IntegerField()
    msetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    qsetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    ssetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    asetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    bsetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    tsetupfee = models.DecimalField(max_digits=10, decimal_places=2)
    monthly = models.DecimalField(max_digits=10, decimal_places=2)
    quarterly = models.DecimalField(max_digits=10, decimal_places=2)
    semiannually = models.DecimalField(max_digits=10, decimal_places=2)
    annually = models.DecimalField(max_digits=10, decimal_places=2)
    biennially = models.DecimalField(max_digits=10, decimal_places=2)
    triennially = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblpricing'


class TblproductDownloads(models.Model):
    product_id = models.IntegerField()
    download_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproduct_downloads'


class TblproductGroupFeatures(models.Model):
    product_group_id = models.IntegerField()
    feature = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproduct_group_features'


class TblproductUpgradeProducts(models.Model):
    product_id = models.IntegerField()
    upgrade_product_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproduct_upgrade_products'


class Tblproductconfiggroups(models.Model):
    name = models.TextField()
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblproductconfiggroups'


class Tblproductconfiglinks(models.Model):
    gid = models.IntegerField()
    pid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfiglinks'


class Tblproductconfigoptions(models.Model):
    gid = models.IntegerField()
    optionname = models.TextField()
    optiontype = models.TextField()
    qtyminimum = models.IntegerField()
    qtymaximum = models.IntegerField()
    order = models.IntegerField()
    hidden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfigoptions'


class Tblproductconfigoptionssub(models.Model):
    configid = models.IntegerField()
    optionname = models.TextField()
    sortorder = models.IntegerField()
    hidden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblproductconfigoptionssub'


class Tblproductgroups(models.Model):
    name = models.TextField()
    headline = models.TextField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)
    orderfrmtpl = models.TextField()
    disabledgateways = models.TextField()
    hidden = models.IntegerField()
    order = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproductgroups'


class Tblproducts(models.Model):
    type = models.TextField()
    gid = models.IntegerField()
    name = models.TextField()
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
    affiliatepayamount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.IntegerField()
    retired = models.IntegerField()
    is_featured = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproducts'


class Tblpromotions(models.Model):
    code = models.TextField()
    type = models.TextField()
    recurring = models.IntegerField(blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    cycles = models.TextField()
    appliesto = models.TextField()
    requires = models.TextField()
    requiresexisting = models.IntegerField()
    startdate = models.DateField()
    expirationdate = models.DateField(blank=True, null=True)
    maxuses = models.IntegerField()
    uses = models.IntegerField()
    lifetimepromo = models.IntegerField()
    applyonce = models.IntegerField()
    newsignups = models.IntegerField()
    existingclient = models.IntegerField()
    onceperclient = models.IntegerField()
    recurfor = models.IntegerField()
    upgrades = models.IntegerField()
    upgradeconfig = models.TextField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblpromotions'


class Tblquoteitems(models.Model):
    quoteid = models.IntegerField()
    description = models.TextField()
    quantity = models.TextField()
    unitprice = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    taxable = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblquoteitems'


class Tblquotes(models.Model):
    subject = models.TextField()
    stage = models.CharField(max_length=9)
    validuntil = models.DateField()
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
    currency = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax1 = models.DecimalField(max_digits=10, decimal_places=2)
    tax2 = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()
    customernotes = models.TextField()
    adminnotes = models.TextField()
    datecreated = models.DateField()
    lastmodified = models.DateField()
    datesent = models.DateField()
    dateaccepted = models.DateField()

    class Meta:
        managed = False
        db_table = 'tblquotes'


class Tblregistrars(models.Model):
    registrar = models.TextField()
    setting = models.TextField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblregistrars'


class Tblrsakeypairs(models.Model):
    identifier = models.CharField(max_length=96)
    private_key = models.TextField()
    public_key = models.TextField()
    algorithm = models.CharField(max_length=16)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblrsakeypairs'


class Tblservergroups(models.Model):
    name = models.TextField()
    filltype = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblservergroups'


class Tblservergroupsrel(models.Model):
    groupid = models.IntegerField()
    serverid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblservergroupsrel'


class Tblservers(models.Model):
    name = models.TextField()
    ipaddress = models.TextField()
    assignedips = models.TextField()
    hostname = models.TextField()
    monthlycost = models.DecimalField(max_digits=10, decimal_places=2)
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


class Tblserversssoperms(models.Model):
    server_id = models.IntegerField()
    role_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblserversssoperms'


class Tblsslorders(models.Model):
    userid = models.IntegerField()
    serviceid = models.IntegerField()
    addon_id = models.IntegerField()
    remoteid = models.TextField()
    module = models.TextField()
    certtype = models.TextField()
    configdata = models.TextField()
    completiondate = models.DateTimeField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblsslorders'


class Tbltask(models.Model):
    priority = models.IntegerField()
    class_name = models.CharField(max_length=255)
    is_enabled = models.IntegerField()
    is_periodic = models.IntegerField()
    frequency = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltask'


class TbltaskStatus(models.Model):
    task_id = models.PositiveIntegerField()
    in_progress = models.IntegerField()
    last_run = models.DateTimeField()
    next_due = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltask_status'


class Tbltax(models.Model):
    level = models.IntegerField()
    name = models.TextField()
    state = models.TextField()
    country = models.TextField()
    taxrate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tbltax'


class TblticketWatchers(models.Model):
    ticket_id = models.PositiveIntegerField()
    admin_id = models.PositiveIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblticket_watchers'
        unique_together = (('ticket_id', 'admin_id'),)


class Tblticketbreaklines(models.Model):
    breakline = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketbreaklines'


class Tblticketdepartments(models.Model):
    name = models.TextField()
    description = models.TextField()
    email = models.TextField()
    clientsonly = models.TextField()
    piperepliesonly = models.TextField()
    noautoresponder = models.TextField()
    hidden = models.TextField()
    order = models.IntegerField()
    host = models.TextField()
    port = models.TextField()
    login = models.TextField()
    password = models.TextField()
    feedback_request = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblticketdepartments'


class Tblticketescalations(models.Model):
    name = models.TextField()
    departments = models.TextField()
    statuses = models.TextField()
    priorities = models.TextField()
    timeelapsed = models.IntegerField()
    newdepartment = models.TextField()
    newpriority = models.TextField()
    newstatus = models.TextField()
    flagto = models.TextField()
    notify = models.TextField()
    addreply = models.TextField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tblticketescalations'


class Tblticketfeedback(models.Model):
    ticketid = models.IntegerField()
    adminid = models.IntegerField()
    rating = models.IntegerField()
    comments = models.TextField()
    datetime = models.DateTimeField()
    ip = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketfeedback'


class Tblticketlog(models.Model):
    date = models.DateTimeField()
    tid = models.IntegerField()
    action = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketlog'


class Tblticketmaillog(models.Model):
    date = models.DateTimeField()
    to = models.TextField()
    name = models.TextField()
    email = models.TextField()
    subject = models.TextField()
    message = models.TextField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketmaillog'


class Tblticketnotes(models.Model):
    ticketid = models.IntegerField()
    admin = models.TextField()
    date = models.DateTimeField()
    message = models.TextField()
    attachments = models.TextField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tblticketnotes'


class Tblticketpredefinedcats(models.Model):
    parentid = models.IntegerField()
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketpredefinedcats'


class Tblticketpredefinedreplies(models.Model):
    catid = models.IntegerField()
    name = models.TextField()
    reply = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketpredefinedreplies'


class Tblticketreplies(models.Model):
    tid = models.IntegerField()
    userid = models.IntegerField()
    contactid = models.IntegerField()
    name = models.TextField()
    email = models.TextField()
    date = models.DateTimeField()
    message = models.TextField()
    admin = models.TextField()
    attachment = models.TextField()
    rating = models.IntegerField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tblticketreplies'


class Tbltickets(models.Model):
    tid = models.CharField(max_length=128, blank=True, null=True)
    did = models.IntegerField()
    userid = models.IntegerField()
    contactid = models.IntegerField()
    name = models.TextField()
    email = models.TextField()
    cc = models.TextField()
    c = models.TextField()
    date = models.DateTimeField()
    title = models.TextField()
    message = models.TextField()
    status = models.CharField(max_length=64)
    urgency = models.TextField()
    admin = models.TextField()
    attachment = models.TextField()
    lastreply = models.DateTimeField()
    flag = models.IntegerField()
    clientunread = models.IntegerField()
    adminunread = models.TextField()
    replyingadmin = models.IntegerField()
    replyingtime = models.DateTimeField()
    service = models.TextField()
    merged_ticket_id = models.IntegerField()
    editor = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'tbltickets'


class Tblticketspamfilters(models.Model):
    type = models.CharField(max_length=7)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblticketspamfilters'


class Tblticketstatuses(models.Model):
    title = models.CharField(max_length=64)
    color = models.TextField()
    sortorder = models.IntegerField()
    showactive = models.IntegerField()
    showawaiting = models.IntegerField()
    autoclose = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblticketstatuses'


class Tbltickettags(models.Model):
    ticketid = models.IntegerField()
    tag = models.TextField()

    class Meta:
        managed = False
        db_table = 'tbltickettags'


class TbltldCategories(models.Model):
    category = models.CharField(max_length=255)
    is_primary = models.IntegerField()
    display_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltld_categories'


class TbltldCategoryPivot(models.Model):
    tld_id = models.IntegerField()
    category_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltld_category_pivot'


class Tbltlds(models.Model):
    tld = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbltlds'


class Tbltodolist(models.Model):
    date = models.DateField()
    title = models.TextField()
    description = models.TextField()
    admin = models.IntegerField()
    status = models.TextField()
    duedate = models.DateField()

    class Meta:
        managed = False
        db_table = 'tbltodolist'


class Tbltransientdata(models.Model):
    name = models.CharField(max_length=1024)
    data = models.TextField()
    expires = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbltransientdata'


class Tblupdatehistory(models.Model):
    admin_id = models.IntegerField()
    original_version = models.CharField(max_length=255)
    new_version = models.CharField(max_length=255)
    success = models.IntegerField()
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblupdatehistory'


class Tblupdatelog(models.Model):
    instance_id = models.CharField(max_length=255)
    level = models.PositiveIntegerField()
    message = models.TextField()
    extra = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblupdatelog'


class Tblupgrades(models.Model):
    userid = models.IntegerField()
    orderid = models.IntegerField()
    type = models.CharField(max_length=13)
    date = models.DateField()
    relid = models.IntegerField()
    originalvalue = models.TextField()
    newvalue = models.TextField()
    new_cycle = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    days_remaining = models.IntegerField()
    total_days_in_cycle = models.IntegerField()
    new_recurring_amount = models.DecimalField(max_digits=10, decimal_places=2)
    recurringchange = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=9)
    paid = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tblupgrades'


class Tblwhoislog(models.Model):
    date = models.DateTimeField()
    domain = models.TextField()
    ip = models.TextField()

    class Meta:
        managed = False
        db_table = 'tblwhoislog'
