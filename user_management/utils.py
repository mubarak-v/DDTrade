# my_app/utils.py

def calculate_percentage(a, b, decimals=2):
    
    if b == 0:
        return None  
    return round((a / b) * 100, decimals)


