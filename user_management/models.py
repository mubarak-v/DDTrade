from django.db import models
from django.contrib.auth.hashers import make_password
import uuid
# Create your models here.
# email mubarak@gmail.com
# pass mubarak
# username mubarak

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from main.models import Stock


def generate_transaction_id():

    # Check if there are any transactions
    last_transaction = TransactionDetails.objects.order_by('-created_at').first()

    if last_transaction:
        # Increment the last transaction ID
        new_id = int(last_transaction.transaction_id) + 1
    else:
        # Start from a base value if no transactions exist
        new_id = 1000000000

    return str(new_id)


# Generate a 10-digit number
class AccountDetailsManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class AccountDetails(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    phone_number = models.CharField(_('Phone Number'), max_length=15, blank=True, null=True)
    password = models.CharField(_('Password'), max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AccountDetailsManager()

    USERNAME_FIELD = 'email'  # Field used for authentication
    REQUIRED_FIELDS = ['username']  # Additional required fields

    def __str__(self):
        return self.username



class Wallet(models.Model):
    Wallet_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10000000,decimal_places=2,default=0.00)
    account = models.ForeignKey(AccountDetails, on_delete=models.CASCADE, related_name="wallet")
# transaction

class TransactionDetails(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('purchase', 'Purchase'),
    ]
    transaction_id = models.CharField(
        max_length=10,
        unique=True,
        default=generate_transaction_id,
        editable=False
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Adjust max_digits
    Wallet = models.ForeignKey(Wallet, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.transaction_type}"

    class Meta:
        ordering = ['-created_at']


class HoldingStock(models.Model):
    STATUS_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('complete', 'Complete'),
        
    ]
    wallet = models.ForeignKey(Wallet,  on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity =models.CharField(max_length=20000)
    average_price = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='buy')
    inversted_amount = models.DecimalField(max_digits=10000000, decimal_places=2,default=0 )
    current_price = models.DecimalField(max_digits=10000000, decimal_places=2, default=0)
# inversted_amount
class InverstedAmount(models.Model):
    Wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    inversted_amount = models.DecimalField(max_digits=10000000, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    current_amount = models.DecimalField(max_digits=10000000,decimal_places=2)