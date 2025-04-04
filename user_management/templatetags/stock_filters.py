from decimal import ROUND_HALF_UP, Decimal
from django import template
from datetime import datetime, timedelta
from main.models import StockDetails
from user_management.models import Wallet
register = template.Library()

@register.simple_tag
def calculate_profit_or_loss(current_price, average_price, quantity):
    """
    Custom template tag to calculate profit or loss.

    Parameters:
    current_price (Decimal): Last traded price (LTP)
    average_price (Decimal): Average buying price
    quantity (int): Quantity of shares held

    Returns:
    float: Profit or loss value.
    """
    try:
        return (float(current_price) - float(average_price)) * int(quantity)
    except (ValueError, TypeError):
        return 0
@register.simple_tag
def calculate_percentage(current_price, average_price, decimals=2):
    """
    Calculate the percentage change between two prices.

    Parameters:
    current_price (float): The current price (e.g., LTP)
    average_price (float): The average buying price
    decimals (int): Number of decimal places for the result

    Returns:
    float: Percentage change rounded to the specified decimals, or None if average_price is 0.
    """
    try:
        if average_price == 0:
            return None  # Avoid division by zero
        percentage_change = ((current_price - average_price) / average_price) * 100
        return round(percentage_change, decimals)
    except (ValueError, TypeError):
        return None
@register.simple_tag
def calculate_diff(current_price, average_price, decimals=2):
    try:
        if average_price == 0:
            return None  # Avoid division by zero
        diff = current_price - average_price
        return round(diff, decimals)
    except (ValueError, TypeError):
        return None


@register.simple_tag
def get_stock_price_difference(stock_name):
    # Get today's date
    today = datetime.today()
    # Get yesterday's date
    yesterday = today - timedelta(days=1)
    
    # Get today's stock details for the given stock_name
    today_stock = StockDetails.objects.filter(date=today, stock__yfinance_name=stock_name).first()
    # Get yesterday's stock details for the same stock_name
    yesterday_stock = StockDetails.objects.filter(date=yesterday, stock__yfinance_name=stock_name).first()
    
    if today_stock and yesterday_stock:
        # Calculate the price difference (percentage change)
        price_diff = ((today_stock.closing_price - yesterday_stock.closing_price) / yesterday_stock.closing_price) * 100
        return round(price_diff, 2)
    return 0.00  # If no data found, return None or 0 depending on your preference

@register.simple_tag(takes_context=True)
def portfolio_current_amount(context):
    holding_stocks = context.get('holdingStock', [])
    total_current_amount = Decimal(0)

    for stock in holding_stocks:
        current_price = Decimal(stock.current_price)  # Ensure current_price is Decimal
        quantity = Decimal(stock.quantity)  # Ensure quantity is Decimal
        total_current_amount += current_price * quantity

    return total_current_amount



@register.simple_tag(takes_context=True)
def portfolio_current_PandL(context):
    Invested_amount = Decimal(context.get('Invested_amount', 0))
    current_amount = Decimal(portfolio_current_amount(context))  # Ensure portfolio_current_amount returns Decimal

    if Invested_amount == 0:  # Handle division by zero
        return Decimal('0.00')

    total_PandL_percentage = ((  Invested_amount- current_amount) / Invested_amount) * 100
    
    return round(total_PandL_percentage,2)

@register.simple_tag(takes_context=True)
def portfolio_PandL_amount(context):
    Invested_amount = Decimal(context.get('Invested_amount', 0))
    current_amount = Decimal(portfolio_current_amount(context))  # Ensure portfolio_current_amount returns Decimal

    PandL_amount = Invested_amount - current_amount
    print(f"pandl = {PandL_amount}")
    return round(PandL_amount,2)