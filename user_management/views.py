from django.shortcuts import render

# Create your views here.

def holdings(request):
    return render(request,'holdings.html')