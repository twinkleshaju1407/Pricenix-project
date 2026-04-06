"""
UiPath Bot Manager
====================
High-level functions to trigger UiPath bots, track their status,
and process results back into the Django dynamic pricing system.

Includes DEMO MODE: when UiPath credentials are placeholders,
the system simulates bot execution for project demonstration.
"""

import json
import random
import uuid
from django.conf import settings
from django.utils import timezone
from .models import Product, UiPathLog
from .uipath_client import UiPathClient
from .pricing_engine import evaluate_price, analyze_sentiment


# --------------------------------------------------
# AVAILABLE BOT PROCESSES
# --------------------------------------------------
UIPATH_PROCESSES = {
    "scraper": {
        "name": "CompetitorPriceScraper",
        "display": "Competitor Price Scraper",
        "description": "Scrapes competitor websites for current product prices using UiPath browser automation.",
        "icon": "🔍",
    },
    "price_update": {
        "name": "DynamicPriceUpdater",
        "display": "Dynamic Price Updater",
        "description": "Evaluates pricing rules and proposes new prices based on competitor data.",
        "icon": "💰",
    },
    "approval_bot": {
        "name": "PriceApprovalBot",
        "display": "Price Approval Bot",
        "description": "Automates the price approval workflow — reviews proposals and sends notifications.",
        "icon": "✅",
    },
}


# --------------------------------------------------
# CHECK IF DEMO MODE
# --------------------------------------------------
def is_demo_mode():
    """Returns True if UiPath credentials are placeholders (demo mode)."""
    client_id = getattr(settings, "UIPATH_CLIENT_ID", "your-client-id")
    return client_id in ("your-client-id", "", None)


def get_uipath_client():
    """Create and authenticate a UiPath client."""
    client = UiPathClient()
    authenticated = client.authenticate()
    return client, authenticated


# --------------------------------------------------
# TRIGGER A BOT
# --------------------------------------------------
def trigger_uipath_bot(process_key):
    """
    Trigger a UiPath bot by its process key (e.g. 'scraper', 'price_update').

    In DEMO MODE: simulates the bot execution with realistic results.
    In LIVE MODE: connects to UiPath Orchestrator.

    Returns:
        (UiPathLog, error_message)
    """
    if process_key not in UIPATH_PROCESSES:
        return None, f"Unknown process: {process_key}"

    process_info = UIPATH_PROCESSES[process_key]
    process_name = process_info["name"]

    # ========== DEMO MODE ==========
    if is_demo_mode():
        return _trigger_demo_bot(process_key, process_name)

    # ========== LIVE MODE (with demo fallback) ==========
    return _trigger_live_bot(process_key, process_name)


def _trigger_demo_bot(process_key, process_name):
    """Simulate a UiPath bot run for demo/college project purposes."""

    demo_job_key = f"DEMO-{uuid.uuid4().hex[:12].upper()}"

    # Create log entry
    log = UiPathLog.objects.create(
        process_name=process_name,
        job_key=demo_job_key,
        status="SUCCESSFUL",
        completed_at=timezone.now(),
    )

    # Generate realistic simulated results
    result_data = _generate_demo_results(process_key)
    log.result_data = result_data
    log.save()

    # Apply simulated results to products
    _apply_demo_results(process_key, result_data)

    return log, None


def _trigger_live_bot(process_key, process_name):
    """
    Trigger a real UiPath bot via Orchestrator API.
    Falls back to demo mode if authentication or job start fails.
    """

    # Try to authenticate with UiPath
    client, authenticated = get_uipath_client()

    if not authenticated:
        # Fallback to demo simulation
        print("[UiPath] Auth failed — falling back to demo simulation")
        return _trigger_demo_bot(process_key, process_name)

    input_args = _build_input_arguments(process_key)
    job_key = client.start_job(process_name, input_args)

    if job_key:
        log = UiPathLog.objects.create(
            process_name=process_name,
            job_key=job_key,
            status="RUNNING",
        )
        return log, None
    else:
        # No process published — fallback to demo simulation
        print("[UiPath] Job start failed — falling back to demo simulation")
        return _trigger_demo_bot(process_key, process_name)


# --------------------------------------------------
# DEMO RESULT GENERATORS
# --------------------------------------------------
def _generate_demo_results(process_key):
    """Generate realistic simulated bot results."""

    products = Product.objects.all()

    if process_key == "scraper":
        scraped = []
        sentiment_samples = [
            "Great value for money, highly recommended!",
            "The price is a bit high compared to others but the quality is good.",
            "Average product, nothing special.",
            "Really disappointed with the recent price hike.",
            "Best deals I've found so far!",
            "Competitor has a much better price.",
            "Market sentiment seems neutral for this category.",
            "People are loving the new features despite the price.",
        ]
        for p in products:
            # Simulate competitor price as ±5–15% of our price
            variation = random.uniform(-0.15, 0.05)
            competitor_price = round(p.our_price * (1 + variation), 2)
            
            # Generate simulated sentiment
            sentiment_text = random.choice(sentiment_samples)
            score, label = analyze_sentiment(sentiment_text)

            scraped.append({
                "id": p.id,
                "name": p.name,
                "price": competitor_price,
                "source": p.competitor_url or "https://competitor-site.com",
                "scraped_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sentiment_score": score,
                "sentiment_label": label,
            })
        return {
            "scraped_prices": scraped,
            "total_scraped": len(scraped),
            "bot_runtime_seconds": round(random.uniform(12, 45), 1),
            "mode": "DEMO",
        }

    elif process_key == "price_update":
        updated = []
        for p in products:
            if p.competitor_price:
                new_price, price_gap = evaluate_price(p.our_price, p.competitor_price)
                updated.append({
                    "id": p.id,
                    "name": p.name,
                    "our_price": p.our_price,
                    "competitor_price": p.competitor_price,
                    "proposed_price": new_price,
                    "price_gap": price_gap,
                })
        return {
            "updated_prices": updated,
            "total_evaluated": len(updated),
            "bot_runtime_seconds": round(random.uniform(5, 20), 1),
            "mode": "DEMO",
        }

    elif process_key == "approval_bot":
        pending = Product.objects.filter(approved=False, proposed_price__isnull=False)
        reviewed = []
        for p in pending:
            reviewed.append({
                "id": p.id,
                "name": p.name,
                "proposed_price": p.proposed_price,
                "action": "notified_admin",
            })
        return {
            "reviewed_products": reviewed,
            "total_reviewed": len(reviewed),
            "notifications_sent": len(reviewed),
            "bot_runtime_seconds": round(random.uniform(3, 10), 1),
            "mode": "DEMO",
        }

    return {"mode": "DEMO", "message": "No action taken"}


def _apply_demo_results(process_key, result_data):
    """Apply simulated results to Product records."""

    if process_key == "scraper" and "scraped_prices" in result_data:
        for item in result_data["scraped_prices"]:
            try:
                product = Product.objects.get(id=item["id"])
                product.competitor_price = float(item["price"])
                
                # Apply sentiment from bot results
                if "sentiment_score" in item:
                    product.sentiment_score = item["sentiment_score"]
                if "sentiment_label" in item:
                    product.sentiment_label = item["sentiment_label"]

                # Auto-evaluate new pricing
                new_price, _ = evaluate_price(product.our_price, product.competitor_price)
                product.proposed_price = new_price
                product.approved = False
                product.rejected = False
                product.save()
            except (Product.DoesNotExist, KeyError, ValueError):
                continue

    elif process_key == "price_update" and "updated_prices" in result_data:
        for item in result_data["updated_prices"]:
            try:
                product = Product.objects.get(id=item["id"])
                product.proposed_price = float(item["proposed_price"])
                product.approved = False
                product.rejected = False
                product.save()
            except (Product.DoesNotExist, KeyError, ValueError):
                continue


# --------------------------------------------------
# BUILD INPUT ARGUMENTS
# --------------------------------------------------
def _build_input_arguments(process_key):
    """Build input arguments for a UiPath process based on current product data."""

    if process_key == "scraper":
        products = Product.objects.filter(competitor_url__isnull=False).exclude(
            competitor_url=""
        )
        return {
            "products": json.dumps(
                [
                    {"id": p.id, "name": p.name, "url": p.competitor_url}
                    for p in products
                ]
            )
        }

    elif process_key == "price_update":
        products = Product.objects.all()
        return {
            "products": json.dumps(
                [
                    {
                        "id": p.id,
                        "name": p.name,
                        "our_price": p.our_price,
                        "competitor_price": p.competitor_price,
                    }
                    for p in products
                ]
            )
        }

    elif process_key == "approval_bot":
        pending = Product.objects.filter(approved=False, proposed_price__isnull=False)
        return {
            "pending_products": json.dumps(
                [
                    {
                        "id": p.id,
                        "name": p.name,
                        "our_price": p.our_price,
                        "proposed_price": p.proposed_price,
                    }
                    for p in pending
                ]
            )
        }

    return {}


# --------------------------------------------------
# CHECK JOB STATUS
# --------------------------------------------------
def check_job_status(job_key):
    """
    Poll UiPath Orchestrator for job status and update the local log.
    In demo mode, jobs complete instantly so this just returns the log.

    Returns:
        (UiPathLog, error_message)
    """
    try:
        log = UiPathLog.objects.get(job_key=job_key)
    except UiPathLog.DoesNotExist:
        return None, f"No log found for job key: {job_key}"

    if log.status in ("SUCCESSFUL", "FAULTED"):
        return log, None  # Already completed

    # Demo jobs are already marked complete
    if is_demo_mode():
        return log, None

    client, authenticated = get_uipath_client()
    if not authenticated:
        return log, "Authentication failed"

    result = client.get_job_status(job_key)
    state = result.get("state", "Unknown")

    # Map UiPath states to our status
    state_map = {
        "Pending": "PENDING",
        "Running": "RUNNING",
        "Successful": "SUCCESSFUL",
        "Faulted": "FAULTED",
        "Stopped": "FAULTED",
    }

    log.status = state_map.get(state, "RUNNING")

    if log.status in ("SUCCESSFUL", "FAULTED"):
        log.completed_at = timezone.now()

        if log.status == "SUCCESSFUL":
            output = client.get_job_output(job_key)
            log.result_data = output
        else:
            log.error_message = result.get("info", "Job faulted without details")

    log.save()
    return log, None


# --------------------------------------------------
# PROCESS BOT RESULTS
# --------------------------------------------------
def process_bot_results(job_key):
    """
    Parse completed bot output and update Product records.

    Returns:
        (count_updated, error_message)
    """
    try:
        log = UiPathLog.objects.get(job_key=job_key)
    except UiPathLog.DoesNotExist:
        return 0, "Log not found"

    if log.status != "SUCCESSFUL" or not log.result_data:
        return 0, "Job not completed or no result data"

    results = log.result_data
    count = 0

    # Handle scraper results: update competitor prices
    if "scraped_prices" in results:
        for item in results["scraped_prices"]:
            try:
                product = Product.objects.get(id=item["id"])
                product.competitor_price = float(item["price"])

                # Auto-evaluate pricing
                new_price, price_gap = evaluate_price(
                    product.our_price, product.competitor_price
                )
                product.proposed_price = new_price
                product.approved = False
                product.rejected = False
                product.save()
                count += 1
            except (Product.DoesNotExist, KeyError, ValueError):
                continue

    # Handle price update results
    if "updated_prices" in results:
        for item in results["updated_prices"]:
            try:
                product = Product.objects.get(id=item["id"])
                product.proposed_price = float(item["proposed_price"])
                product.approved = False
                product.rejected = False
                product.save()
                count += 1
            except (Product.DoesNotExist, KeyError, ValueError):
                continue

    return count, None
