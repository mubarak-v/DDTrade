from django.contrib import admin
from .models import AccountDetails,Wallet,TransactionDetails


# Register your models here.
admin.site.register(Wallet)
admin.site.register(AccountDetails)
admin.site.register(TransactionDetails)
