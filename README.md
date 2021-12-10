SUPPORTED RESOURCES
===================

The current WHMCSync app supports the following:

* Clients
* Clients groups
* Client contacts
* Servers
* Servers groups
* Products
* Product groups
* Product prices
* Services
* Services hosting account settings
* Cancellation requests
* Currencies
* Hosting accounts
* Tax rules



WHMCS TO FLEIO SYNC INSTALLATION
================================

Create a new database, call it *whmcs* and copy the actual WHMCS database here.
This new database will be used to copy all the informations we need.

Add the database in Fleio settings.py:

```python
DATABASES = {
    'default': {
        # default fleio database settings
    },
    'whmcs': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'WHMCS',
         'USER': 'root',
         'PASSWORD': '',
         'HOST': 'localhost',
         'OPTIONS': {'charset': 'utf8mb4'}
         }
    }
```

Add the database router in settings.py

```python

# WHMCSYNC settings

INSTALLED_APPS += ('whmcsync.whmcsync', )
DATABASE_ROUTERS = ['whmcsync.whmcsync.routers.WhmcSyncRouter']
AUTHENTICATION_BACKENDS = ('whmcsync.whmcsync.auth_backend.WhmcSyncAuthBackend',
                           'django.contrib.auth.backends.ModelBackend')
    
```

NOTES
=====

The *whmcs_models.py* file contains the Django models representation from WHMCS.
If you wish to import additional data, these models will help.
After installing this app, do not forget to run **django migrate** to setup the new whmcsync database in Fleio.
This database is used to allow authentication for users with their old password.

To import tickets, ticket replies & ticket notes attachments, add the attachments' dir from whmcs at the 
same location as this readme (after adding repo files to fleio installation).

To see import options, activate Fleio environment and run `django whmcsync -h`.


### Known limitations

#### Staff users:

- staff users are imported as inactive, so super admins in Fleio can review their permissions

#### Servers:

- passwords are not synced, they have to be re-set

#### Tax rules:

- tax rules that apply to all countries in WHMCS are not imported since Fleio does not support this

#### Tickets

- ! importing tickets works only using Fleio 2022.01.1 and above
- tickets, ticket replies & notes created by admins will match staff users in fleio by their related 
WHMCS admin field which represents first name and last name of the admin at the date of creation of 
the ticket/reply/note
- Fleio does not support multiple predefined reply categories using the same name so only the 
first by ID category from WHMCS will be imported with related predefined replies
