import datetime
from datetime import timedelta, date
from decimal import Decimal
from pyexpat.errors import messages

from celery import shared_task
from django.shortcuts import redirect


from main.models import Stock, StockDetails
from user_management.models import HoldingStock, StockTransaction, Wallet
from . models import  StocksignalResult
from . strategies import get_stock_signal, ut_bot
def execute_strategy():
    from .models import TradingAlgorithm
    stocks = Stock.objects.all()
    
    tradingalgorithm = TradingAlgorithm.objects.all()
    for algorithm in tradingalgorithm:
        strategy_function = globals().get(algorithm.function_name)
        if strategy_function is None:
            print(f"Error: No function found for algorithm {algorithm.function_name}")
            continue  
        
        print(f"Strategy function: {strategy_function}")
        
        for stock in stocks:
            result = strategy_function(stock.name)
            
            stocksignalResult= StocksignalResult(stock=stock, tradingAlgorithm=algorithm, signal=result)
            stocksignalResult.save()
            
            print(f"stock_name: {stock.name},function name:{stock.name} result: {result}")


from django.utils import timezone

from decimal import Decimal
from django.utils import timezone

from decimal import Decimal
from django.utils import timezone
@shared_task
def execute_subscribed_trades():
    print("functon is alog ")
    wallet = Wallet.objects.all()
    # today = timezone.now().date()  # Use timezone-aware date
    today = date(2024,12,13)
    for w in wallet:
        algorithm = w.selected_trading_algorithm
        stocksignal_results = StocksignalResult.objects.filter(
            tradingAlgorithm=algorithm,
            created_at__date=today  # Use the __date lookup to match the date part
        )

        for s in stocksignal_results:
            # buy signals 
            if s.signal == "natural":
                # Ensure s.stock is a Stock instance
                try:
                    stock_instance = s.stock if isinstance(s.stock, Stock) else Stock.objects.get(name=str(s.stock))
                except Stock.DoesNotExist:
                    print(f"Stock not found for signal result: {s}")
                    continue

                stock_details = StockDetails.objects.filter(date=today, stock=stock_instance)

                for stock in stock_details:
                    holding_stock = HoldingStock.objects.filter(wallet=w, stock=stock_instance, status="buy").first()
                    closing_price = stock.closing_price
                    if w.amount < Decimal(closing_price):
                        print(f"Not enough funds to purchase stock: {stock_instance.name}")
                        continue
                    else:
                        # Deduct wallet amount
                        w.amount -= Decimal(closing_price)
                        w.save()

                        def create_transaction():
                            StockTransaction.objects.create(
                                wallet=w,
                                stock=stock_instance,
                                transaction_type='buy',
                                quantity=1,
                                price=closing_price,
                            )

                        if holding_stock:
                            holding_stock.quantity = int(holding_stock.quantity) + 1  # Ensure quantity is an integer
                            holding_stock.inversted_amount += closing_price
                            holding_stock.average_price = (
                                holding_stock.inversted_amount / holding_stock.quantity
                            )
                            holding_stock.current_price = closing_price
                            holding_stock.save()
                            create_transaction()
                        else:
                            HoldingStock.objects.create(
                                wallet=w,
                                stock=stock_instance,
                                quantity=1,
                                average_price=closing_price,
                                status='buy',
                                inversted_amount=closing_price,
                                current_price=closing_price
                            )
                            create_transaction()

                        print(f"Stock purchased: {stock_instance.name} at {closing_price}, selected algo {s.tradingAlgorithm.name}")

            elif s.signal == "sell":
                # Ensure s.stock is a Stock instance
                try:
                    stock_instance = s.stock if isinstance(s.stock, Stock) else Stock.objects.get(name=str(s.stock))
                except Stock.DoesNotExist:
                    print(f"Stock not found for signal result: {s}")
                    continue

                stock_details = StockDetails.objects.filter(date=today, stock=stock_instance)
                closing_price = None
                for stock in stock_details:
                    closing_price = stock.closing_price

                if closing_price is None:
                    print(f"Closing price not found today : {stock_instance.name}")
                    continue

                # Check if the user holds the stock
                holding_stock = HoldingStock.objects.filter(wallet=w, stock=stock_instance, status="buy").first()

                if not holding_stock or int(holding_stock.quantity) <= 0:  # Convert quantity to int
                    print(f"No stock available to sell: {stock_instance.name}")
                    continue

                # Add the sale amount to wallet
                w.amount += closing_price
                w.save()

                # Update or remove the holding
                holding_stock.quantity = int(holding_stock.quantity) - 1  # Convert to int before subtraction
                holding_stock.inversted_amount -= closing_price

                if holding_stock.quantity == 0:
                    # If all stocks are sold, delete the record
                    holding_stock.delete()
                else:
                    # Update the record for remaining holdings
                    holding_stock.current_price = closing_price
                    holding_stock.save()

                # Log the transaction
                StockTransaction.objects.create(
                    wallet=w,
                    stock=stock_instance,
                    transaction_type='sell',
                    quantity=1,
                    price=closing_price,
                )

                print(f"Stock sold: {stock_instance.name} at {closing_price}")

            else:
                print(f"Signal not natural for stock: {s.stock}")
