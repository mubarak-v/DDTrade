import yfinance as yf
import matplotlib.pyplot as plt
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

def getStock():
    today = datetime.today()
    start_date = today - timedelta(days=30)
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))
    start_date = today - timedelta(days=60)
    try:
        for ticker in stock_names:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=today)
            if not hist.empty:
                open_price = hist['Close'].iloc[0]
                close_price = round(hist['Close'].iloc[-1], 2)
                percentage_change = ((close_price - open_price) / open_price) * 100

                # Ensure the Stock object is correctly fetched or created
                stock_obj, created = Stock.objects.get_or_create(
                    yfinance_name=ticker,
                    defaults={'name': ticker}  # Provide a default name
                )

                # Save StockDetails with valid foreign key and data
                StockDetails.objects.create(
                    stock=stock_obj,  # Valid Stock instance
                    closing_price=close_price,
                    percentage_change=percentage_change
                )
    except Exception as e:
        print(f"Error processing stocks: {e}")
    
def home(request):
    s = Stock.objects.all()
    for stock in s:
        print(stock.name)
    query = request.GET.get('ticker', '').strip().upper()
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))

    today = datetime.today()
    today_stock_details = StockDetails.objects.filter(date=today).order_by('-percentage_change')
    if query:
        filtered_stocks = [ticker for ticker in stock_names if query in ticker.upper()]
    else:
        filtered_stocks = []
    stock_data = []
    if not today_stock_details:
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
    today = datetime.today()
    ticker = request.GET.get('ticker', '').strip().upper()
    stockDetails = StockDetails.objects.filter(stock__yfinance_name=ticker,date=today)
    print(stockDetails)
    for i in stockDetails:
        print(i.stock.name)
    context = {
            'stockDetails': stockDetails

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
