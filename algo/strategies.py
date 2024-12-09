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


def get_stock_signal(yfinance_name):
    """
    Generate buy/sell/natural signals for a given stock.
    If yesterday's signal was 'sell', keep showing 'natural' until the next 'buy'.
    If yesterday's signal was 'buy', keep showing 'natural' until the next 'sell'.
    :param yfinance_name: ID of the stock to evaluate
    :return: Signal for today's data ('buy', 'sell', 'natural')
    """
    from datetime import date, timedelta
    import pandas as pd

    today = date.today()
    yesterday = today - timedelta(days=3)

    # Fetch historical data for the stock
    stock_data = StockDetails.objects.filter(stock__yfinance_name=yfinance_name).order_by('date')
    if not stock_data.exists():
        return "No historical data available for the stock."

    # Convert to a DataFrame for analysis
    df = pd.DataFrame.from_records(
        stock_data.values('date', 'closing_price'),
        index='date'
    ).sort_index()

    # Calculate RSI
    df['RSI'] = calculate_rsi(df['closing_price'])

    # Add a column for signals
    df['Signal'] = None

    # Ensure we have data for yesterday
    if yesterday not in df.index:
        return "No data available for yesterday."

    # Iterate through the dataframe to determine signals
    last_signal = "natural"  # Initial state
    for current_date in df.index:
        rsi = df.loc[current_date, 'RSI']

        # Determine the current signal based on RSI
        if rsi < 30:
            current_signal = "buy"
        elif rsi > 70:
            current_signal = "sell"
        else:
            current_signal = "natural"

        # Adjust the signal based on the last signal's state
        if last_signal == "sell" and current_signal == "natural":
            current_signal = "natural"
        elif last_signal == "buy" and current_signal == "natural":
            current_signal = "natural"
        else:
            last_signal = current_signal  # Update last signal if a new one occurs

        # Assign the signal for the current date
        df.loc[current_date, 'Signal'] = current_signal

    # Return the signal for yesterday
    return df.loc[yesterday, 'Signal']

