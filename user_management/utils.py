# my_app/utils.py
from .models import Wallet, HoldingStock
from datetime import datetime, timedelta
from main.models import StockDetails, Stock
import yfinance as yf
from algo.utils import execute_strategy




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
    
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))
    
    try:
        for ticker in stock_names:   
            stock = yf.Ticker(ticker)
            hist = stock.history(start=today, end=today + timedelta(days=1))
            if not hist.empty:
                open_price = hist['Close'].iloc[0]
                close_price = round(hist['Close'].iloc[-1], 2)
                stock  = Stock.objects.filter(yfinance_name=ticker)
                StockDetails.objects.create(
                    stock=stock, 
                    closing_price=close_price,
                    opening_price= open_price               
                )
        updateWalletStockDetails()
        execute_strategy()  
    except Exception as e:
        print(f"Error processing stocks: {e}")


def saveStockHistory(days=90):
    today = datetime.today()
    start_date = today - timedelta(days=days)
    stock_names = list(Stock.objects.values_list('yfinance_name', flat=True))
    
    try:
        for ticker in stock_names:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=today)
            
            if not hist.empty:
                # Ensure open_price is calculated correctly
                open_price = hist['Open'].iloc[0] if 'Open' in hist.columns else None

                for date, row in hist.iterrows():
                    close_price = round(row['Close'], 2)
                    
                    stock_obj, _ = Stock.objects.get_or_create(
                        yfinance_name=ticker,
                    )

                    # Avoid duplicate entries for the same date
                    stock_date = date.date()  # This is the date to store in the database

                    # Ensure that only unique entries are created for each day
                    if not StockDetails.objects.filter(stock=stock_obj, date=stock_date).exists():
                        StockDetails.objects.create(
                            stock=stock_obj,  
                            closing_price=close_price,
                            percentage_change=0,  # This could be computed if needed
                            opening_price=open_price,
                            date=stock_date  
                        )
                        print(f"Stock: {ticker}, Date: {stock_date}, Closing Price: {close_price}")
                    else:
                        print(f"Record for {ticker} on {stock_date} already exists.")
            else:
                print(f"No data available for {ticker} from {start_date} to {today}.")
        
        print(f"{days} days' stock data processed.")
    except Exception as e:
        # Log the error with the actual exception message
        print(f"Error processing stocks for {days} days: {str(e)}")



       
 # Delete all StockDetails records
def deleteAllStockDetails():
    try:
        StockDetails.objects.all().delete()
        print("All StockDetails records have been deleted.")
    except Exception as e:
        print(f"Error deleting StockDetails: {e}")
