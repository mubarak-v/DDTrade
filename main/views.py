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

    ticker = request.GET.get('ticker', '').strip().upper()
    if ticker:
        stock = yf.Ticker(ticker)
        stock_info = stock.history(period="1d")  
        stock_info_details = stock.info

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(stock_info.index, stock_info['Close'], label='Close Price', color='blue', lw=2)
        ax.set_title(f"{ticker} - Stock Price for 1 Day")
        ax.set_xlabel('Time')
        ax.set_ylabel('Price (₹)')
        ax.legend()

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        
        context = {
            'stock_data': {
                'date': stock_info.index[-1].strftime('%Y-%m-%d'),
                'open': stock_info['Open'].iloc[0],
                'close': round(stock_info['Close'].iloc[0], 2),
                'high': stock_info['High'].iloc[0],
                'low': stock_info['Low'].iloc[0],
                'volume': stock_info['Volume'].iloc[0],
                'ticker': ticker,
                'market_cap': stock_info_details.get('marketCap', 'N/A'),
                'dividend_yield': stock_info_details.get('dividendYield', 'N/A'),
                'week_52_high': stock_info_details.get('fiftyTwoWeekHigh', 'N/A'),
                'week_52_low': stock_info_details.get('fiftyTwoWeekLow', 'N/A'),
                'pe_ratio': stock_info_details.get('trailingPE', 'N/A'),
                'beta': stock_info_details.get('beta', 'N/A'),
                'previous_close': stock_info_details.get('previousClose', 'N/A'),
                'country': stock_info_details.get('country', 'N/A'),
                'currency': stock_info_details.get('currency', 'N/A')
            },
            'graph': img_base64,
            
        }
        
        print("Close Price:", context['stock_data']['close'])

    else:
        # If no valid ticker found, return an empty context or an error message
        context = {
            'error': "No stock data available for the provided search query.",
            
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
