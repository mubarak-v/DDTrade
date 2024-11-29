from django.db import models
from django.contrib.auth.hashers import make_password
import uuid
# Create your models here.
# email mubarak@gmail.com
# pass mubarak
# username mubarak

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

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
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10000000, decimal_places=2)
    Wallet = models.ForeignKey(Wallet, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.transaction_type} ({self.status})"

    class Meta:
        ordering = ['-created_at']