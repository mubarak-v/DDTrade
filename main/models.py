from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    yfinance_name = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.name


class StockDetails(models.Model):
    yfinance_name = models.CharField(max_length=50, unique=True) 
    closing_price = models.CharField(max_length=10,)  
    percentage_change = models.DecimalField(max_digits=5, decimal_places=2)  
    date = models.DateField(auto_now_add=True)  

    def __str__(self):
        return f"{self.stock} - {self.type} ({self.date})"
