from datetime import datetime
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
import uuid


from algo.models import TradingTransaction
from .models import HoldingStock, StockTransaction
from decimal import Decimal, InvalidOperation

from main.models import StockDetails,Stock
from .models import Wallet,TransactionDetails
from .utils import calculate_percentage, calculate_profit_or_loss
# Create your views here.   

def holdings(request):
    
    user = request.user
    wallets = Wallet.objects.get(account__username=user.username,selected_wallet  =True )

    
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
            return redirect('home')  
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')


def wallet(request):
    user = request.user
    selected_wallet_query = request.POST.get('selected-account', '')
    selected_wallet_id = request.POST.get('selected-account') if request.method == 'POST' else None

    all_wallets = Wallet.objects.filter(account__username=user.username)

    wallet = None
    if selected_wallet_query:
        wallet = all_wallets.filter(Wallet_id=selected_wallet_query).first()
        if wallet:
            all_wallets.update(selected_wallet=False)  
            wallet.selected_wallet = True
            wallet.save()
        else:
            print(f"No wallet found with ID {selected_wallet_query} for user {user.username}.")
    else:
        wallet = all_wallets.filter(selected_wallet=True).first()
        if not wallet and all_wallets.exists():
            wallet = all_wallets.first()
            wallet.selected_wallet = True
            wallet.save()

    transactions = []
    if wallet:
        transactions = TransactionDetails.objects.filter(Wallet=wallet)

    context = {
        'wallets': wallet,  
        'transactions': transactions,  
        'has_wallet': wallet is not None, 
        'request': request,  
        'all_wallets': all_wallets, 
        'selected_wallet_id': wallet.Wallet_id if wallet else None 
    }

    return render(request, 'wallet.html', context)


def createWallet(request):
    query  = request.POST.get('wallet_name', '')
    print(query)
    user = request.user
    wallet = Wallet.objects.create(account=user,name = query)
    return redirect('wallet')



def buyStock(request):

    def generate_stock_transaction_identity_code():
        """Generates a unique stock transaction identity code"""
        date_str = datetime.now().strftime("%Y%m%d")  # Use datetime without prefix
        return f"TXN{date_str}-{uuid.uuid4().hex[:6].upper()}"

    identity_code = generate_stock_transaction_identity_code()
    user = request.user
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    qty = request.GET.get('qty', '1')
    

    
    wallets = Wallet.objects.get(account__username=user.username, selected_wallet=True)
    stock = Stock.objects.get(yfinance_name=ticker)
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker, date=today)
    if not stockDetails:
        return HttpResponse("You do not have this stock to buy.", status=400)
    else:

        closing_price = ""
        for price in stockDetails:
                closing_price = price.closing_price
                holding_stock = HoldingStock.objects.filter(wallet=wallets, stock=stock, status="buy").first()
                total_price = Decimal(closing_price)*Decimal(qty)
        if wallets.amount <  total_price:
            
            return HttpResponse("Insufficient funds", status=400)
        else:

            
            wallets.amount -= total_price

            wallets.save()  # save                            

            def createTransaction():
                stockTransaction = StockTransaction.objects.create(
                    wallet=wallets,
                    stock=stock,
                    transaction_type='buy',
                    quantity =qty, 
                    price=closing_price,
                    stock_transaction_identity_code = identity_code
                )
            # if holding_stock:
            #         holding_stock.quantity = int(holding_stock.quantity) + qty
            #         holding_stock.inversted_amount += closing_price
            #         holding_stock.stock_transaction_identity_code += identity_code 
            #         holding_stock.average_price = (
            #         holding_stock.inversted_amount / holding_stock.quantity
                    

            #         )
                    
            #         holding_stock.current_price = closing_price
            #         holding_stock.save()
            #         createTransaction()
            # else:
            HoldingStock.objects.create(
                            stock_transaction_identity_code = identity_code,
                            wallet=wallets,
                            stock=stock,
                            quantity=qty,  
                            average_price=closing_price,
                            status='buy', 
                            inversted_amount=total_price,
                            current_price = closing_price
                        )
            createTransaction()

    return redirect('holdings')
def sellStock(request):
    
    from datetime import datetime 
   
    user = request.user
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    
    
    qty = int(request.GET.get('qty', '1'))
   
    print(f"qty = {qty}")
    
    wallets = Wallet.objects.get(account__username=user.username, selected_wallet=True)
    stock = Stock.objects.get(yfinance_name=ticker)
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker, date=today)
    

    
    closing_price = None
    for price in stockDetails:
        closing_price = Decimal(price.closing_price)
    
    
    if closing_price is None:
        # Handle case where closing price is not available
        return HttpResponse("Stock closing price not found for today.", status=400)
    
    # Check if the user holds the stock
    holding_stock = HoldingStock.objects.filter(wallet=wallets, stock=stock, status="buy").first()
    
    if not holding_stock or int(holding_stock.quantity) <= 0:  # Convert quantity to int
        # Handle case where no stock is available to sell
        return HttpResponse("You do not have this stock to sell.", status=400)
    
    def stock_transaction():
        StockTransaction.objects.create(
            wallet = wallets, 
            stock = stock, 
            transaction_type= 'sell', 
            quantity = qty, 
            price = closing_price, 
            stock_transaction_identity_code =holding_stock.stock_transaction_identity_code


        )
        print(holding_stock.stock_transaction_identity_code)
    
    
    total_price = closing_price *qty
    # Update or remove the holding
    if int(holding_stock.quantity) < qty:
        # If the user tries to sell more stock than they have, return an error
        return HttpResponse(f"Your account has only {holding_stock.quantity} shares to sell", status=400)
    
    holding_stock.quantity = int(holding_stock.quantity) - qty  # Convert to int before subtraction
    holding_stock.inversted_amount -= total_price

    
    # Add the sale amount to wallet
    wallets.amount += total_price
    wallets.save()
    
    if holding_stock.quantity == 0:
        # If all stocks are sold, delete the record
        holding_stock.delete()
    else:
        # Update the record for remaining holdings
        holding_stock.current_price = closing_price
        holding_stock.save()
    stock_transaction()
    
    # Redirect to holdings or any other view
    return redirect('holdings')




def transaction(request):
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
            wallet = Wallet.objects.get(account__username=user, selected_wallet=True)
            
            
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

    return redirect("wallet")



def account(request):

    stockTransaction  = StockTransaction.objects.all()
    context = {
        "stock_transaction": stockTransaction
    }
    return render(request, "account.html", context)