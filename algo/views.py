from django.shortcuts import render
from . utils import execute_strategy
from algo.models import TradingAlgorithm
from main.models import StockDetails,Stock
# Create your views here.

def algoMain(request):
   
    return render(request, 'algo_main.html')