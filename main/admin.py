from django.contrib import admin

# Register your models here.
from .models import Stock, StockDetails


admin.site.register(StockDetails)
admin.site.register(Stock)

