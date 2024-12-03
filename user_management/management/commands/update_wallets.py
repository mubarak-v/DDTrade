from typing import Any
from django.core.management.base import BaseCommand
from user_management.utils import update_all_wallets

class Command(BaseCommand):
    help = "Update all wallets for all users"
    def handle(self, *args, **kwargs):
        result = update_all_wallets()
        self.stdout.write(self.style.SUCCESS(f"Update complete: {result}"))