from django.contrib import admin

from algo.models import TradingAlgorithm, TradingTransaction,Trade,algo_performance

# Register your models here.
admin.site.register(TradingAlgorithm)
admin.site.register(TradingTransaction)
admin.site.register(Trade)
admin.site.register(algo_performance)