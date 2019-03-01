from django.contrib import admin

from .models import SyncedAccount


class SyncedAccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')


admin.site.register(SyncedAccount, SyncedAccountAdmin)
