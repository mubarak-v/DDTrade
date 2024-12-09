from django.shortcuts import render
from . utils import execute_strategy

from algo.models import TradingAlgorithm
from main.models import StockDetails,Stock
# Create your views here.

def algoMain(request):
    
    
    execute_strategy()
        

    
        

    stockDetails = Stock.objects.all()
    for s in stockDetails:
        name = s.yfinance_name
        # print(f"stock:{name}, {get_stock_signal(name)}")
    return render(request, 'algo_main.html')