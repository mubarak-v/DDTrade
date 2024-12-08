from django.shortcuts import render

from algo.models import TradingAlgorithm
from main.models import StockDetails,Stock
# Create your views here.

def algoMain(request):
    tradingalgorithm = TradingAlgorithm.objects.all()
    # function_name = ''
    # for trade in tradingalgorithm:
    #     print(f"algorithm:{trade.name}")
    #     function_name = trade.name

    stockDetails = Stock.objects.all()
    for s in stockDetails:
        name = s.yfinance_name
        # print(f"stock:{name}, {get_stock_signal(name)}")
    return render(request, 'algo_main.html')