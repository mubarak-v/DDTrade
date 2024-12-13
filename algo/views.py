from django.shortcuts import redirect, render

from user_management.models import Wallet
from . utils import execute_strategy, execute_subscribed_trades
from algo.models import TradingAlgorithm
from main.models import StockDetails,Stock
from user_management.utils import saveStockHistory
# Create your views here.

def algoMain(request):
    execute_subscribed_trades()
    user = request.user

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

        

