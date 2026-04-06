from .models import Product
from .crawler import crawl_competitor_site
from .pricing_engine import evaluate_price
from .email_utils import send_price_approval_email


def run_dynamic_pricing():
    """
    Automated dynamic pricing workflow
    """

    products = Product.objects.all()

    for product in products:
        competitor_price = crawl_competitor_site(product)

        new_price, price_gap = evaluate_price(
            product.our_price,
            competitor_price
        )

        # Update product with proposal
        product.competitor_price = competitor_price
        product.proposed_price = new_price
        product.approved = False
        product.rejected = False
        product.save()

        # Send detailed approval email
        send_price_approval_email(
            product=product,
            price_gap=price_gap
        )
