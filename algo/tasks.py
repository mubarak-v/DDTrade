from celery import shared_task



@shared_task
def execute_subscribed_trades_task():
    from algo.utils import execute_subscribed_trades
    execute_subscribed_trades()



@shared_task
def getStock_task():
    from user_management.utils import getStock
    getStock()

@shared_task
def updateWalletStockDetails_task():
    from user_management.utils import updateWalletStockDetails
    updateWalletStockDetails()

@shared_task
def print_L():
    print("Hello, I'm a print_L task.")
    return 0

@shared_task
def execute_strategy_task():
    from algo.utils import execute_strategy
    execute_strategy()
