from django.contrib import admin
from .models import AccountDetails,Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(AccountDetails)
