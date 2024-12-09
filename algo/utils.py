from main.models import Stock
from . models import  StocksignalResult
from . strategies import get_stock_signal
def execute_strategy():
    from . models import TradingAlgorithm
    stocks = Stock.objects.all()
    
    tradingalgorithm = TradingAlgorithm.objects.all()
    for algorithm in tradingalgorithm :
        strategy_function = globals().get(algorithm.name)
        
        for stock in stocks :
           
            result  = strategy_function(stock.name)
            print(result)
            if 'buy' or 'sell' or 'Natural':
                print(f"stock_name:{stock.name},result:{result}")
                stocksignalResult = StocksignalResult()
                stocksignalResult.stock = stock
                stocksignalResult.tradingAlgorithm = algorithm
                stocksignalResult.signal = result
                stocksignalResult.save()
            else :
                stocksignalResult = StocksignalResult()
                stocksignalResult.stock = stock
                stocksignalResult.tradingAlgorithm = algorithm
                stocksignalResult.signal = "notfound"
                stocksignalResult.save()

    
   
    

    
    

     
        
    