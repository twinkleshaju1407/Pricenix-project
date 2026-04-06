from .scrapy_scraper import scrapy_scrape_price
from .selenium_scraper import selenium_scrape_price


def crawl_competitor_site(product):
    """
    Hybrid scraper:
    1. Try Scrapy (fast)
    2. Fallback to Selenium (dynamic)
    """

    if not product.competitor_url:
        return product.our_price

    # Try Scrapy first
    price = scrapy_scrape_price(product.competitor_url)
    if price:
        return price

    # Fallback to Selenium
    price = selenium_scrape_price(product.competitor_url)
    if price:
        return price

    # Final fallback
    return product.our_price
