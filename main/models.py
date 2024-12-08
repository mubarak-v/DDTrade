from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    yfinance_name = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.name


class StockDetails(models.Model):
    
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        blank=True  )
    closing_price = models.DecimalField(max_digits=10, decimal_places=2)  # Adjusted for numeric data
    percentage_change = models.DecimalField(max_digits=5, decimal_places=2)  
    date = models.DateField()  # Keeps the default of auto-setting the creation date

    def __str__(self):
        return f"{self.stock.name} on {self.date}: {self.closing_price}"
