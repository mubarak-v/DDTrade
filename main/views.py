import yfinance as yf
import matplotlib.pyplot as plt
from django.shortcuts import render
import io
import urllib
import base64
from datetime import datetime, timedelta
from .models import Stock, StockDetails

def home(request):
    query = request.GET.get('ticker', '').strip().upper()
    stock_names = [
        "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
        "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
        "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
        "HINDALCO.NS", "HINDUNILVR.NS", "HDFC.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS",
        "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
        "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS",
        "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
    ]

    if query:
        filtered_stocks = [ticker for ticker in stock_names if query in ticker.upper()]
        print(f"Filtered stocks: {filtered_stocks}")
    else:
        filtered_stocks = []
        print("No stocks found")
    print(query)

    stock_data = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    try:
        for ticker in stock_names:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                open_price = hist['Close'].iloc[0]  
                close_price = round(hist['Close'].iloc[-1],2)  
                percentage_change = ((close_price - open_price) / open_price) * 100
                # StockDetails(
                #     stock=Stock.objects.get_or_create(yfinance_name=ticker),
                #     closing_price=close_price,
                #     percentage_change=percentage_change,
                #     date=end_date
                # )
                # StockDetails.save()
                stock_data.append({
                    'ticker': ticker,
                    'price': close_price,
                    'percentage_change': percentage_change
                })
                
                
    except Exception as e:
        print(f"Error fetching stock data: {e}")

    stock_data_sorted = sorted(stock_data, key=lambda x: x['percentage_change'], reverse=True)
    top_gainers = stock_data_sorted[:20]  
    top_losers = stock_data_sorted[-20:]  
    
    context = {
            'filtered_stocks': filtered_stocks,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
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





