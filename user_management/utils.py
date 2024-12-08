# my_app/utils.py
from .models import Wallet, HoldingStock
from datetime import datetime, timedelta
from main.models import StockDetails, Stock
import yfinance as yf


def calculate_percentage(a, b, decimals=2):
    
    if b == 0:
        return None  
    return round((a / b) * 100, decimals)


def calculate_profit_or_loss(ltp, avg, qty):
    """
    Calculate profit or loss.

    Parameters:
    ltp (float): Last traded price (LTP)
    avg (float): Average buying price (AVG)
    qty (int): Quantity of shares or units held

    Returns:
    float: Profit or loss value rounded to 2 decimal places.
    """
    profit_or_loss = (ltp - avg) * qty
    return round(profit_or_loss, 2)

def updateWalletStockDetails():
    wallet = Wallet.objects.all()
    today = datetime.today()
    holdingStock = HoldingStock.objects.all()
    for stock in holdingStock:
        stock_details = StockDetails.objects.filter(stock__yfinance_name=stock.stock.yfinance_name, date = today )
        for stock_d in stock_details:
            stock.current_price =stock_d.closing_price
            stock.save()

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
        updateWalletStockDetails()
    except Exception as e:
        print(f"Error processing stocks: {e}")


# save stock history
def saveStockHistory(days=90):
    today = datetime.today()
    start_date = today - timedelta(days=days)  
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))
    
    try:
        for ticker in stock_names:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=today)
            if not hist.empty:
                for date, row in hist.iterrows():
                    close_price = round(row['Close'], 2)
                    
                    stock_obj, created = Stock.objects.get_or_create(
                        yfinance_name=ticker,
                    )

                    if not StockDetails.objects.filter(stock=stock_obj, date=date.date()).exists():
                        StockDetails.objects.create(
                            stock=stock_obj,  
                            closing_price=close_price,
                            percentage_change=0,  
                            date=date.date()  
                        )
                        print(f"stock:{ticker}, close_price:{close_price},date:{date}")
                    else:
                        print(f"Record for {ticker} on {date.date()} already exists.")
        print("Three months' stock data processed.")
    except Exception as e:
        print(f"Error processing stocks for three months: {e}")

       
 # Delete all StockDetails records
def deleteAllStockDetails():
    try:
        StockDetails.objects.all().delete()
        print("All StockDetails records have been deleted.")
    except Exception as e:
        print(f"Error deleting StockDetails: {e}")
