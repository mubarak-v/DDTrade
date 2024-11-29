from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Wallet
# Create your views here.   

def holdings(request):
    return render(request,'holdings.html')

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
    
    wallet = Wallet.objects.get(account__email =user)
    TransactionDetails = TransactionDetails.objects.get(wallet = wallet)
    print(wallet)
    return render(request,'wallet.html')