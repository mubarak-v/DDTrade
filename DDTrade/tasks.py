from celery import shared_task
from algo.utils import execute_subscribed_trades


@shared_task
def execute_subscribed_trades_task():
    from algo.utils import execute_subscribed_trades
    execute_subscribed_trades()
@shared_task
def print_p():
    print("Hello, I'm a print_p task.")
    return 0

def execute_strategy_tsk():
    from algo.utils import execute_strategy
    execute_strategy()