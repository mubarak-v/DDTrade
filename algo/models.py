from django.db import models

# Create your models here.

class TradingAlgorithm(models.Model):
    name = models.CharField(max_length=100,  unique=True)
    description = models.TextField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TradingTransaction(models.Model):
    TradingAlgorithm = models.ForeignKey(TradingAlgorithm, related_name='transactions', on_delete = models.CASCADE)

    trasaction_type = models.CharField(choices=(('BUY', 'Buy'), ('SELL', 'Sell')), max_length=5 )
