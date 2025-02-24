import datetime
from typing import Counter
from django.shortcuts import redirect, render
from datetime import datetime, timedelta

from algo.strategies import get_stock_signal, ut_bot
from user_management.models import Wallet
from . utils import execute_strategy, execute_subscribed_trades, run_execute_subscribed_trades_for_days, run_strategy_for_days
from algo.models import StocksignalResult, TradingAlgorithm
from main.models import StockDetails,Stock
from user_management.utils import deleteAllStockDetails, saveStockHistory
# Create your views here.
        # Get the function_name of the selected trading algorithm

def algoMain(request):
    

    # saveStockHistory(120)
    # print(get_stock_signal('ZOMATO.NS',(2024,12,10)))
    # execute_strategy((2024,12,5))
    # deleteAllStockDetails()
        # saveStockHistory()
    # run_strategy_for_days(70)
    # execute_subscribed_trades((2024,12,2))
    # print(ut_bot('ZOMATO.NS',(2024,11,12)))
    # run_execute_subscribed_trades_for_days(120)
    # saveStockHistory(120)
    stock_t= StockDetails.objects.filter(stock__yfinance_name = 'APOLLOHOSP.NS')
    # if stock_t.exists:
    #     for stock in stock_t:
    #         print(f'{stock.date} , {stock.closing_price}')
    # else:
    #     print('No stock data available')
    # stockS  = StocksignalResult.objects.all()
    # for sss in stockS:
    #     print(f'{sss.stock.yfinance_name} , {sss.signal}')
    buy_count = StocksignalResult.objects.filter(signal__iexact='buy').count()
    sell_count = StocksignalResult.objects.filter(signal__iexact='sell').count()
    natural_count = StocksignalResult.objects.filter(signal__iexact='natural').count()

    print(f"Buy signals: {buy_count}")
    print(f"Sell signals: {sell_count}")
    print(f"Natural signals: {natural_count}")


# Count signals
   # 1. Check total records
    # total_records = StocksignalResult.objects.count()
    # print(f"Total records in StocksignalResult: {total_records}")

    # # 2. Check distinct signals
    # distinct_signals = StocksignalResult.objects.values_list('signal', flat=True).distinct()
    # print("Distinct signals:", list(distinct_signals))

    # # 3. Count signals with case-insensitive filtering
    # buy_count = StocksignalResult.objects.filter(signal__iexact='buy').count()
    # sell_count = StocksignalResult.objects.filter(signal__iexact='sell').count()
    # neutral_count = StocksignalResult.objects.filter(signal__iexact='neutral').count()

    # # Print results
    # print(f"Buy signals: {buy_count}")
    # print(f"Sell signals: {sell_count}")
    # print(f"Neutral signals: {neutral_count}")

    # # 4. Debug a few rows
    # example_rows = StocksignalResult.objects.all()[:5]
    # for row in example_rows:
    #     print(f"Stock: {row.stock.name}, Algorithm: {row.tradingAlgorithm.name}, Signal: {row.signal}")


    user = request.user
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    # Get the wallet where selected_wallet is True
    wallet = Wallet.objects.filter(account=user, selected_wallet=True).first()  # Use `.first()` to get a single wallet, or handle if no wallet is found
    
    if wallet:  # Ensure we have a valid wallet
        # Get the function_name of the selected trading algorithm
        subscribed_algo = wallet.selected_trading_algorithm.function_name if wallet.selected_trading_algorithm else None
        print(f"Algorithm subscribed: {subscribed_algo}")
    else:
        subscribed_algo = None
        print("No wallet found or no selected wallet.")

    # Get all trading algorithms
    tradingAlgorithm = TradingAlgorithm.objects.all()

    # Check if the algorithm function_name matches the subscribed_algo
    for al in tradingAlgorithm:
        if al.function_name == subscribed_algo:
            print(f"Algorithm subscribed is {subscribed_algo}")

    # Pass the data to the context for rendering
    context = {
        'wallet': wallet,  # Pass the selected wallet, or None if no wallet is found
        'tradingAlgorithm': tradingAlgorithm,
        'subscribed_algo': subscribed_algo  # Pass the subscribed algorithm function_name
    }

    return render(request, 'algo_main.html', context)


def subscribeToAlgo (request):

    if request.method == "POST":
        wallet = Wallet.objects.get(account = request.user, selected_wallet = True)
        alogrithmQuery = request.POST.get('algorithm', '')

        if alogrithmQuery:
            try:
                algorithm  = TradingAlgorithm.objects.get(function_name=alogrithmQuery)
                wallet.selected_trading_algorithm = algorithm
                wallet.save()

                print(f"Algorithm {algorithm.name} subscribed successfully.")
            except TradingAlgorithm.DoesNotExist:
                    print(f"Algorithm with ID {alogrithmQuery} does not exist.")    
            print(alogrithmQuery)
        else:
            print(f"algorithm not found")
    return redirect('algoMain')

def unsubscribeToAlgo(request):
    if request.method == "POST":
        wallet = Wallet.objects.get(account=request.user, selected_wallet=True)
        # Make sure to use the correct key ('un-algorithm') in the POST request
        alogrithmQuery = request.POST.get('un-algorithm', '')  
        print(f"Algorithm to unsubscribe: {alogrithmQuery}")  # Check if the algorithm name is coming through

        if alogrithmQuery:
            try:
                # Look for the algorithm by its function_name
                algorithm = TradingAlgorithm.objects.get(function_name=alogrithmQuery)
                # Update wallet to indicate no algorithm is selected
                wallet.selected_trading_algorithm = None  # or 'null' if needed
                wallet.save()

                print(f"Algorithm {algorithm.name} unsubscribed successfully.")
            except TradingAlgorithm.DoesNotExist:
                print(f"Algorithm with function_name {alogrithmQuery} does not exist.")
        else:
            print(f"Algorithm not found in the request.")

    return redirect('algoMain')

        


