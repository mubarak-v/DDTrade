from main.models import Stock
from . models import  StocksignalResult
from . strategies import get_stock_signal, ut_bot
def execute_strategy():
    from .models import TradingAlgorithm
    stocks = Stock.objects.all()
    
    tradingalgorithm = TradingAlgorithm.objects.all()
    for algorithm in tradingalgorithm:
        strategy_function = globals().get(algorithm.name)
        if strategy_function is None:
            print(f"Error: No function found for algorithm {algorithm.name}")
            continue  
        
        print(f"Strategy function: {strategy_function}")
        
        for stock in stocks:
            result = strategy_function(stock.name)
            
            stocksignalResult= StocksignalResult(stock=stock, tradingAlgorithm=algorithm, signal=result)
            stocksignalResult.save()
            
            print(f"stock_name: {stock.name},function name:{stock.name} result: {result}")
    