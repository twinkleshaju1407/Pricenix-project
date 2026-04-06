from pricing.auto_update import run_dynamic_pricing


def scheduled_price_check():
    """
    Cron job entry point
    """
    run_dynamic_pricing()
