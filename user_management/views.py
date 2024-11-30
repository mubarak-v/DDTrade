from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import HoldingStock

from main.models import StockDetails,Stock
from .models import Wallet,TransactionDetails
# Create your views here.   

def holdings(request):
    user = request.user
    wallets = Wallet.objects.get(account__username=user.username)
    holdingStock = HoldingStock.objects.filter(wallet = wallets)
    
    context = {
        'holdingStock':holdingStock
    }
    for i in holdingStock:
        print(i.average_price)
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
    print(user)

    # Filter wallets for the logged-in user
    wallets = Wallet.objects.filter(account__username=user.username)

    if wallets.exists():
        # Take the first wallet
        wallet = wallets.first()

        # Deposit 500 to the wallet
        wallet.amount += 500
        wallet.save()

        # Log the transaction
        transaction = TransactionDetails.objects.create(
            Wallet=wallet,
            amount=500,
            transaction_type='deposit'
        )
        print(f"Transaction logged: {transaction.transaction_id}")

        # Fetch all transactions for this wallet
        transactions = TransactionDetails.objects.filter(Wallet=wallet)
        for transaction in transactions:
            print(f"Transaction ID: {transaction.transaction_id}, Amount: {transaction.amount}")

    else:
        print("No wallet found for the user.")

    # Pass wallets to the template
    context = {
        'wallets': wallets[0],
        'transactions': transactions

               }
    return render(request, 'wallet.html', context)


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

    holding = HoldingStock.objects.create(
        wallet=wallets,
        stock=stock,
        quantity=1,  # Assuming you are buying 1 unit, adjust as necessary
        average_price=closing_price,
        status='buy',  # Marking as a "buy" action
    )

    # Redirect to 'holdings.html' or any other view
    return redirect('holdings')
