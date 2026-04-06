from django.core.mail import send_mail
from django.conf import settings


def send_price_approval_email(product, price_gap):
    subject = "Price Change Approval Required"

    message = f"""
PRODUCT PRICE CHANGE REQUEST

Product Name: {product.name}

Current Price: ₹{product.our_price}
Competitor Price: ₹{product.competitor_price}

Price Gap Detected: ₹{price_gap}

Pricing Rule Applied:
- Maximum 3% discount allowed
- Final proposed price respects competitor pricing

Proposed New Price: ₹{product.proposed_price}

Action Required:
Please log in to the admin dashboard to approve or reject this price update.

Regards,
Dynamic Pricing System
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        ['pricinglist6@gmail.com'],  # replace with real email
        fail_silently=False
    )
