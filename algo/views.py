from django.shortcuts import render
from . utils import execute_strategy
from algo.models import TradingAlgorithm
from main.models import StockDetails,Stock
# Create your views here.

def algoMain(request):
    stockDetails = StockDetails.objects.filter(stock__yfinance_name = "LICI.NS")
    for s in stockDetails:
        print(f"stock:{s.stock.yfinance_name}, {s.closing_price}, date{s.date}")
    
    execute_strategy()
        

    
        

    
    return render(request, 'algo_main.html')