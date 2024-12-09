from django.contrib import admin

from algo.models import StocksignalResult, TradingAlgorithm, TradingTransaction,Trade,algo_performance

# Register your models here.
admin.site.register(TradingAlgorithm)
admin.site.register(TradingTransaction)
admin.site.register(Trade)
admin.site.register(algo_performance)
admin.site.register(StocksignalResult)