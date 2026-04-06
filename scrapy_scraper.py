import requests
from parsel import Selector
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrapy_scrape_price(url):
    """
    Scrapes price from static HTML using Scrapy selectors
    """

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        selector = Selector(text=response.text)

        price_text = selector.css("span.price::text").get()

        if price_text:
            price = re.sub(r"[^\d]", "", price_text)
            return float(price)

    except Exception as e:
        print("Scrapy error:", e)

    return None
