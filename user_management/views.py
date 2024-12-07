from datetime import datetime
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import HoldingStock, StockTransaction
from decimal import Decimal, InvalidOperation

from main.models import StockDetails,Stock
from .models import Wallet,TransactionDetails
from .utils import calculate_percentage, calculate_profit_or_loss
# Create your views here.   

def holdings(request):
    user = request.user
    wallets = Wallet.objects.get(account__username=user.username)
    holdingStock = HoldingStock.objects.filter(wallet = wallets)
    Invested_amount= 0
    for stock in holdingStock:
         Invested_amount += stock.inversted_amount
    print(Invested_amount)

    
    context = {
        'holdingStock':holdingStock,
        'Invested_amount':Invested_amount , 
        'calculate_profit_or_loss':calculate_profit_or_loss ,
        'request':request
    }
    
    return render(request,'holdings.html',context)

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your target view
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')


def wallet(request):
    user = request.user
    

    # Filter wallets for the logged-in user
    wallets = Wallet.objects.filter(account__username=user.username)
    wallet = None
    transactions = []
    print

    if wallets.exists():
        # Take the first wallet
        wallet = wallets.first()

        

        # Fetch all transactions for this wallet
        transactions = TransactionDetails.objects.filter(Wallet=wallet)
        
        wallets = wallets[0]
    else:
        print("No wallet found for the user.")

    # Pass wallets to the template
    context = {
        'wallets': wallets,
        'transactions': transactions, 
        'has_wallet': wallet is not None, 
        'request':request

               }
    return render(request, 'wallet.html', context)
def createWallet(request):
    user = request.user
    wallet = Wallet.objects.create(account=user)
    return redirect('wallet')



def buyStock(request):
    user = request.user
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    wallets = Wallet.objects.get(account__username=user.username)
    stock = Stock.objects.get(yfinance_name=ticker)
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker, date=today)
    
    closing_price = ""
    for price in stockDetails:
        closing_price = price.closing_price
    holding_stock = HoldingStock.objects.filter(wallet=wallets, stock=stock, status="buy").first()
    wallets.amount -= Decimal(closing_price)

    wallets.save()  # save                            

    def createTransaction():
        stockTransaction = StockTransaction.objects.create(
            wallet=wallets,
            stock=stock,
            transaction_type='buy',
            quantity =1, 
            price=closing_price,
        )
    if holding_stock:
            # Update existing holding
            holding_stock.quantity = int(holding_stock.quantity) + 1
            holding_stock.inversted_amount += closing_price
            holding_stock.average_price = (
            holding_stock.inversted_amount / holding_stock.quantity
             

            )
            holding_stock.current_price = closing_price
            holding_stock.save()
            createTransaction()
    else:
            # Create a new holding
            HoldingStock.objects.create(
                wallet=wallets,
                stock=stock,
                quantity=1,  # Buying 1 unit, adjust as necessary
                average_price=closing_price,
                status='buy',  # Marking as a "buy" action
                inversted_amount=closing_price,
                current_price = closing_price
            )
            createTransaction()

    # Redirect to 'holdings.html' or any other view
    return redirect('holdings')
def sellStock(request):
    from datetime import datetime  # Ensure you import datetime if not already
    user = request.user
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    
    # Fetch user wallet and stock details
    wallets = Wallet.objects.get(account__username=user.username)
    stock = Stock.objects.get(yfinance_name=ticker)
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker, date=today)
    
    # Fetch the closing price
    closing_price = None
    for price in stockDetails:
        closing_price = price.closing_price
    
    if closing_price is None:
        # Handle case where closing price is not available
        return HttpResponse("Stock closing price not found for today.", status=400)
    
    # Check if the user holds the stock
    holding_stock = HoldingStock.objects.filter(wallet=wallets, stock=stock, status="buy").first()
    
    if not holding_stock or int(holding_stock.quantity) <= 0:  # Convert quantity to int
        # Handle case where no stock is available to sell
        return HttpResponse("You do not have this stock to sell.", status=400)
    
    # Add the sale amount to wallet
    wallets.amount += closing_price
    wallets.save()
    
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
    
    # Redirect to holdings or any other view
    return redirect('holdings')




def transaction(request):
    print("functin working....")
    if request.method == 'POST':  # Ensure we process only POST requests
        transactionType = request.POST.get('transaction', '')
        amount = request.POST.get('amount', '').strip()  # Strip whitespace from input

        print(f"Transaction: {transactionType}, Amount: {amount}")

        try:
            # Validate and convert the amount to Decimal
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'Insufficient funds')
                return redirect("wallet")

            user = request.user
            wallet = Wallet.objects.get(account__username=user)

            if transactionType == 'deposit':
                print(f"Deposit: {amount}")
                wallet.amount += amount
                wallet.save()
                TransactionDetails.objects.create(
                    Wallet=wallet,
                    amount=amount,
                    transaction_type='deposit'
                )
                return redirect("wallet")

            elif transactionType == 'withdrawal':
                if wallet.amount >= amount:
                    wallet.amount -= amount
                    wallet.save()
                    TransactionDetails.objects.create(
                        Wallet=wallet,
                        amount=amount,
                        transaction_type='withdrawal'
                    )
                    return redirect("wallet")
                else:
                    messages.error(request, 'Insufficient funds')
        except InvalidOperation:
            messages.error(request, 'Invalid amount entered. Please enter a valid number.')
        except Wallet.DoesNotExist:
            messages.error(request, 'Wallet not found')

    # Redirect to a fallback page or wallet overview in case of an error
    return redirect("wallet")
