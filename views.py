import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Sum, Q
from .models import Product, PriceHistory, UiPathLog


# ==============================
# DASHBOARD VIEW
# ==============================
def dashboard(request):
    products = Product.objects.all()

    # Fetch latest price history for analytics chart
    history = PriceHistory.objects.select_related("product").order_by("-date")[:10]

    product_names = []
    old_prices = []
    new_prices = []

    for record in history:
        product_names.append(record.product.name)
        old_prices.append(float(record.old_price))
        new_prices.append(float(record.new_price))

    # Revenue Simulation
    total_revenue = sum([
        (p.our_price * p.sales_count) if hasattr(p, "sales_count") else 0
        for p in products
    ])

    # Approval stats
    approved_count = products.filter(approved=True).count()
    pending_count = products.filter(approved=False).count()

    # Sentiment Distribution
    sentiment_counts = {
        "Positive": products.filter(sentiment_label="Positive").count(),
        "Neutral": products.filter(sentiment_label="Neutral").count(),
        "Negative": products.filter(sentiment_label="Negative").count(),
    }

    # Market Position (Our Price vs Competitor Price)
    market_position = [
        {"name": p.name, "our": p.our_price, "comp": p.competitor_price or 0}
        for p in products
    ]

    context = {
        "products": products,
        "total_revenue": total_revenue,
        "approved_count": approved_count,
        "pending_count": pending_count,
        "product_names_json": json.dumps(product_names),
        "old_prices_json": json.dumps(old_prices),
        "new_prices_json": json.dumps(new_prices),
        "sentiment_counts_json": json.dumps(sentiment_counts),
        "market_position_json": json.dumps(market_position),
        "has_history": len(product_names) > 0,
    }

    return render(request, "admin_dashboard.html", context)


# ==============================
# APPROVE PRICE
# ==============================
# def approve_price(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if product.proposed_price:
#         # Save approval in history
#         PriceHistory.objects.create(
#             product=product,
#             old_price=product.our_price,
#             new_price=product.proposed_price,
#             status="APPROVED"
#         )

#         # Update product price
#         product.our_price = product.proposed_price
#         product.approved = True
#         product.rejected = False
#         product.proposed_price = None
#         product.save()

#     return redirect("dashboard")
from django.core.mail import send_mail
from django.conf import settings

def approve_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.proposed_price:
        # Save history
        PriceHistory.objects.create(
            product=product,
            old_price=product.our_price,
            new_price=product.proposed_price,
            status="APPROVED"
        )

        # Update product
        old_price = product.our_price
        new_price = product.proposed_price

        product.our_price = new_price
        product.approved = True
        product.rejected = False
        product.proposed_price = None
        product.save()

        # ✅ SEND EMAIL
        send_mail(
            subject="✅ Price Approved - Dynamic Pricing System",
            message=f"""
Product: {product.name}

Old Price: ₹{old_price}
New Price: ₹{new_price}

Status: APPROVED

This update has been applied successfully.
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["manager@gmail.com"],  # change this
            fail_silently=False,
        )

    return redirect("dashboard")

# ==============================
# REJECT PRICE
# ==============================
def reject_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.proposed_price:
        # Save rejection in history
        PriceHistory.objects.create(
            product=product,
            old_price=product.our_price,
            new_price=product.proposed_price,
            status="REJECTED"
        )

        product.rejected = True
        product.approved = False
        product.proposed_price = None
        product.save()

    return redirect("dashboard")


# ==============================
# STORE VIEW
# ==============================
def store(request):
    products = Product.objects.filter(approved=True)

    query = request.GET.get("q")
    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    if query:
        products = products.filter(name__icontains=query)

    if min_price:
        products = products.filter(our_price__gte=min_price)

    if max_price:
        products = products.filter(our_price__lte=max_price)

    return render(request, "store.html", {
        "products": products,
        "query": query or "",
        "min_price": min_price or "",
        "max_price": max_price or "",
    })


# ==============================
# PRODUCT DETAIL
# ==============================
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, approved=True)
    return render(request, "product_detail.html", {"product": product})


# ==============================
# SALES SIMULATION (OPTIONAL)
# ==============================
def simulate_sale(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if hasattr(product, "sales_count"):
        product.sales_count += 1
        product.save()

    return redirect("product_detail", product_id=product.id)


# ==============================
# UIPATH DASHBOARD
# ==============================
def uipath_dashboard(request):
    """Render the UiPath bot monitoring dashboard."""
    from .uipath_bot import UIPATH_PROCESSES, is_demo_mode

    logs = UiPathLog.objects.all()[:20]

    # Stats
    total_jobs = UiPathLog.objects.count()
    successful_jobs = UiPathLog.objects.filter(status="SUCCESSFUL").count()
    faulted_jobs = UiPathLog.objects.filter(status="FAULTED").count()
    running_jobs = UiPathLog.objects.filter(status__in=["PENDING", "RUNNING"]).count()

    context = {
        "processes": UIPATH_PROCESSES,
        "logs": logs,
        "total_jobs": total_jobs,
        "successful_jobs": successful_jobs,
        "faulted_jobs": faulted_jobs,
        "running_jobs": running_jobs,
        "demo_mode": is_demo_mode(),
    }

    return render(request, "uipath_dashboard.html", context)


# ==============================
# TRIGGER UIPATH JOB
# ==============================
@require_POST
def trigger_uipath_job(request):
    """API endpoint to trigger a UiPath bot process."""
    from .uipath_bot import trigger_uipath_bot

    process_key = request.POST.get("process_key", "")
    log, error = trigger_uipath_bot(process_key)

    if error:
        return JsonResponse({
            "success": False,
            "error": error,
            "log_id": log.id if log else None,
            "status": log.status if log else "FAULTED",
        })
    
    send_mail(
        subject="🤖 UiPath Bot Triggered",
        message=f"""
Bot Triggered Successfully!

Process: {process_key}
Job Key: {log.job_key}

Status: {log.status}
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=["hibatasneemz12@gmail.com"],  # change this
        fail_silently=False,
    )


    return JsonResponse({
        "success": True,
        "job_key": log.job_key,
        "log_id": log.id,
        "status": log.status,
        "process_name": log.process_name,
        
    })


# ==============================
# UIPATH JOB STATUS (AJAX)
# ==============================
@require_GET
def uipath_job_status(request, job_key):
    """API endpoint to poll the status of a UiPath job."""
    from .uipath_bot import check_job_status

    log, error = check_job_status(job_key)

    if error:
        return JsonResponse({"success": False, "error": error})

    return JsonResponse({
        "success": True,
        "job_key": log.job_key,
        "status": log.status,
        "process_name": log.process_name,
        "triggered_at": log.triggered_at.strftime("%Y-%m-%d %H:%M:%S") if log.triggered_at else None,
        "completed_at": log.completed_at.strftime("%Y-%m-%d %H:%M:%S") if log.completed_at else None,
        "result_data": log.result_data,
        "error_message": log.error_message,
    })


# ==============================
# CHATBOT VIEW (TAVILY AI)
# ==============================
def chatbot(request):
    """
    Handle chatbot messages using Tavily Search API.
    """
    if request.method == "POST":
        import json
        from tavily import TavilyClient
        from django.conf import settings

        try:
            data = json.loads(request.body)
            query = data.get("message", "").strip()
            
            # --- 1. LOCAL DATABASE SEARCH ---
            # Extract keywords (simple split for now)
            keywords = [k for k in query.split() if len(k) > 2]
            local_products = []
            
            if keywords:
                q_objects = Q()
                for kw in keywords:
                    q_objects |= Q(name__icontains=kw)
                
                local_matches = Product.objects.filter(q_objects).distinct()[:5]
                
                if local_matches.exists():
                    reply_parts = ["I found those items on your website:"]
                    for p in local_matches:
                        sentiment_icon = "🟢" if "Positive" in p.sentiment_label else "🔴" if "Negative" in p.sentiment_label else "⚪"
                        reply_parts.append(
                            f"- **{p.name}**: ₹{p.our_price} (Market: ₹{p.competitor_price or 'N/A'}) - Sentiment: {sentiment_icon} {p.sentiment_label}"
                        )
                    reply_parts.append("\nIs there anything else I can help you with regarding these or other products?")
                    return JsonResponse({"success": True, "reply": "\n".join(reply_parts)})

            # --- 2. WEB FALLBACK (TAVILY) ---
            api_key = getattr(settings, "TAVILY_API_KEY", "")
            
            if not api_key or api_key == "tvly-your-api-key-here":
                # Demo Mode Response
                demo_replies = [
                    f"That's a great question about '{query}'. In a real scenario, I would use Tavily to search for live competitor prices and market trends to give you a precise answer.",
                    f"Searching for insights on '{query}'... Based on current simulated trends, prices in this category are expected to stabilize. You might want to monitor competitor shifts closely.",
                    f"I've analyzed the market for '{query}'. Sentiment is currently positive, suggesting a high demand which could support a slight price increase."
                ]
                import random
                return JsonResponse({"success": True, "reply": random.choice(demo_replies)})

            # Real Tavily Search
            tvly = TavilyClient(api_key=api_key)
            # Use 'qna' search for a concise answer
            response = tvly.qna_search(query=query)
            
            return JsonResponse({
                "success": True, 
                "reply": response
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, "chatbot.html")

