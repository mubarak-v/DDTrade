from django.db import models
from django.apps import apps
from main.models import Stock

# Create your models here.
def generate_transaction_id(model_class):
    
    """
    Generates a new transaction ID based on the latest record in the specified model class.

    Args:
        model_class (models.Model): The Django model class to query (e.g., StockTransaction or TransactionDetails).

    Returns:
        str: A new unique transaction ID.
    """
    # Check if there are any transactions for the given model class
    last_transaction = model_class.objects.order_by('-created_at').first()

    if last_transaction:
        # Increment the last transaction ID
        new_id = int(last_transaction.transaction_id) + 1
    else:
        # Start from a base value if no transactions exist
        new_id = 1000000000

    return str(new_id)

class TradingAlgorithm(models.Model):
    name = models.CharField(max_length=100,  unique=True)
    description = models.TextField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TradingTransaction(models.Model):
    transaction_id = models.BigIntegerField(
        unique=True,
        editable=False,
        default=lambda: generate_transaction_id(TradingTransaction)
    )
    trading_algorithm = models.ForeignKey(
        TradingAlgorithm, related_name='transactions', on_delete=models.CASCADE, null=True, blank=True
    )
    transaction_type = models.CharField(
        choices=(('BUY', 'Buy'), ('SELL', 'Sell')), max_length=5
    )

class Trade(models.Model):
    trading_algorithm = models.ForeignKey(
        'algo.TradingAlgorithm', related_name='trading_algorithm', on_delete=models.CASCADE, null=True, blank=True
    )
    wallet = models.ForeignKey(
        'user_management.Wallet', related_name="algo_wallet", on_delete=models.CASCADE
    )
    stock = models.ForeignKey(Stock, related_name="algo_stocks", on_delete=models.CASCADE)

    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        choices=(('ACTIVE', 'Active'), ('CLOSED', 'Closed')), max_length=10
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Use apps.get_model for lazy loading
        Wallet = apps.get_model('user_management', 'Wallet')
        return f"{self.trading_algorithm.name} - {self.stock.yfinance_name}"
   
class algo_performance(models.Model):
    Trade = models.ForeignKey(Trade, related_name='performance', on_delete = models.CASCADE)
    status = models.CharField(choices=(('WIN', 'Win'), ('LOSS', 'loss')), max_length=10)
    profit_or_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
