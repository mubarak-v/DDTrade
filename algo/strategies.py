import pandas as pd
from datetime import timedelta, date
from django.db.models import F

from main.models import StockDetails


def calculate_rsi(series, window=14):
    """
    Calculate the Relative Strength Index (RSI) for a given price series.
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(data, period=1):
    """
    Calculate the Exponential Moving Average (EMA).
    :param data: The price data (series or list).
    :param period: The period for the EMA calculation.
    :return: The EMA values as a pandas Series.
    """
    return data.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=10):
    """
    Calculate the Average True Range (ATR).
    :param df: DataFrame with 'high', 'low', 'close' columns.
    :param period: The period for the ATR calculation.
    :return: The ATR values as a pandas Series.
    """
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = true_range.max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

# def get_stock_signal(yfinance_name):
#     """
#     Generate buy/sell/natural signals for a given stock.
#     If yesterday's signal was 'sell', keep showing 'natural' until the next 'buy'.
#     If yesterday's signal was 'buy', keep showing 'natural' until the next 'sell'.
#     :param yfinance_name: ID of the stock to evaluate
#     :return: Signal for yesterday's data ('buy', 'sell', 'natural')
#     """
#     from datetime import date, timedelta
#     import pandas as pd

#     today = date.today()
    
#     # Try to find the closest available date in the last 6 days
#     stock_data = None
#     for days_back in range(1, 50):  # Start from 1 day back, go up to 6 days back
#         yesterday = today - timedelta(days=days_back)
#         stock_data = StockDetails.objects.filter(stock__yfinance_name=yfinance_name, date=yesterday).order_by('date')
        
#         if stock_data.exists():  # If stock data is found, break out of the loop
#             break
#     else:
#         # If no data was found within the last 6 days, return a message
#         return "No data available for the last 6 days."

#     print(f"Using data from {yesterday}.")  # Output which day we are using
    
#     # Convert to a DataFrame for analysis
#     df = pd.DataFrame.from_records(
#         stock_data.values('date', 'closing_price'),
#         index='date'
#     ).sort_index()

#     # Calculate RSI
#     df['RSI'] = calculate_rsi(df['closing_price'])

#     # Add a column for signals
#     df['Signal'] = None

#     # Ensure we have data for yesterday
#     if yesterday not in df.index:
#         return "No data available for yesterday."

#     # Iterate through the dataframe to determine signals
#     last_signal = "natural"  # Initial state
#     for current_date in df.index:
#         rsi = df.loc[current_date, 'RSI']

#         # Determine the current signal based on RSI
#         if rsi < 30:
#             current_signal = "buy"
#         elif rsi > 70:
#             current_signal = "sell"
#         else:
#             current_signal = "natural"

#         # Adjust the signal based on the last signal's state
#         if last_signal == "sell" and current_signal == "natural":
#             current_signal = "natural"
#         elif last_signal == "buy" and current_signal == "natural":
#             current_signal = "natural"
#         else:
#             last_signal = current_signal  # Update last signal if a new one occurs

#         # Assign the signal for the current date
#         df.loc[current_date, 'Signal'] = current_signal

#     # Return the signal for yesterday
#     return df.loc[yesterday, 'Signal']

def get_stock_signal(yfinance_name):
    """
    Generate buy/sell/natural signals for a given stock.
    If yesterday's signal was 'sell', keep showing 'natural' until the next 'buy'.
    If yesterday's signal was 'buy', keep showing 'natural' until the next 'sell'.
    :param yfinance_name: ID of the stock to evaluate
    :return: Signal for yesterday's data ('buy', 'sell', 'natural')
    """
    today = date.today()
    
    # Try to find the closest available date in the last 6 days
    stock_data = None
    for days_back in range(1, 50):  # Start from 1 day back, go up to 6 days back
        yesterday = today - timedelta(days=days_back)
        stock_data = StockDetails.objects.filter(stock__yfinance_name=yfinance_name, date=yesterday).order_by('date')
        
        if stock_data.exists():  # If stock data is found, break out of the loop
            break
    else:
        # If no data was found within the last 6 days, return a message
        return "No data available for the last 6 days."

    print(f"Using data from {yesterday}.")  # Output which day we are using
    
    # Convert to a DataFrame for analysis
    df = pd.DataFrame.from_records(
        stock_data.values('date', 'high', 'low', 'close'),
        index='date'
    ).sort_index()

    # Calculate ATR and EMA
    atr = calculate_atr(df, period=10)
    df['ema'] = calculate_ema(df['close'], period=1)
    df['xATR'] = atr

    # Initialize signal tracking
    last_signal = 'natural'  # Initial signal state
    df['signal'] = 'natural'  # Default all signals to 'natural'

    # Calculate the trailing stop logic and signals
    for i in range(1, len(df)):
        # Apply the trailing stop logic
        if df['close'][i] > df['xATR'][i]:
            df['signal'][i] = 'buy'
        elif df['close'][i] < df['xATR'][i]:
            df['signal'][i] = 'sell'

        # Maintain the last signal until a change
        if last_signal == 'sell' and df['signal'][i] == 'natural':
            df['signal'][i] = 'natural'
        elif last_signal == 'buy' and df['signal'][i] == 'natural':
            df['signal'][i] = 'natural'
        else:
            last_signal = df['signal'][i]

    # Return the signal for yesterday
    return df.loc[yesterday, 'signal']