from django.contrib import admin
from .models import AccountDetails, HoldingStock, Wallet,TransactionDetails,InverstedAmount


# Register your models here.
admin.site.register(Wallet)
admin.site.register(AccountDetails)
admin.site.register(TransactionDetails)
admin.site.register(HoldingStock)
admin.site.register(InverstedAmount)



