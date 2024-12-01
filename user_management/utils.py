# my_app/utils.py

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
    float: Profit or loss value. Positive indicates profit, negative indicates loss.
    """
    return (ltp - avg) * qty