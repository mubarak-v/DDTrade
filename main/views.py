import yfinance as yf
from django.shortcuts import render
import io
import base64
from datetime import datetime, timedelta
from .models import Stock, StockDetails
from django.http import JsonResponse
from .stock_name import save_stock_data_to_db
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.db.models import Max
from user_management.utils import  getStock, updateWalletStockDetails,deleteAllStockDetails,saveStockHistory


    
def home(request):
    # deleteAllStockDetails()
    # saveStockHistory(30)
    s = Stock.objects.all() 
    query = request.GET.get('ticker', '').strip().upper()
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))

    today = datetime.today()
    last_date = StockDetails.objects.aggregate(Max('date'))['date__max']
    today_stock_details = StockDetails.objects.filter(date=last_date).order_by('-percentage_change')  
    if query:
        filtered_stocks = [ticker for ticker in stock_names if query in ticker.upper()]
    else:
        filtered_stocks = []
    stock_data = []
    
    if datetime.now().weekday() not in [5, 6] and not StockDetails.objects.filter(date=today).order_by('-percentage_change') and datetime.now().time() > datetime.strptime("15:35", "%H:%M").time():
        getStock()
    stock_data_sorted = sorted(stock_data, key=lambda x: x['percentage_change'], reverse=True)
    top_gainers = stock_data_sorted[:20]  
    top_losers = stock_data_sorted[-20:] 
    context = {
            'filtered_stocks': filtered_stocks,
            'top_gainers': today_stock_details,
            
        }
    
    return render(request, 'home.html', context)
def stock(request):
    ticker = request.GET.get('ticker', '').strip().upper()
    latest_date = StockDetails.objects.filter(stock__yfinance_name=ticker).order_by('-date').first()
    if latest_date:
        # Filter the stock details for the most recent date
        stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker, date=latest_date.date)
    else:
        stockDetails = []

    context = {
            'stockDetails': stockDetails,
            'date' : latest_date.date

        }

    return render(request, 'stock_details.html', context)




def fetch_and_save_stocks(request):
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.tickertape.in/screener/equity")

    try:
        save_stock_data_to_db(driver)
        return JsonResponse({"status": "success", "message": "Stock data saved successfully!"})
    finally:
        driver.quit()

def buyStock(request):
    
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker,date=today)
    
    return render(request, 'stock_details.html')
