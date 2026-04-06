from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re


def selenium_scrape_price(url):
    """
    Robust Selenium price scraper for dynamic sites (Amazon-like)
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        price_text = None

        # 🔥 Try multiple selectors (robust strategy)
        selectors = [
            "span.a-price-whole",              # Amazon main
            "span.a-offscreen",                # Amazon hidden full price
            "div._30jeq3._16Jk6d",              # Flipkart style
            "span.price",                      # Generic
        ]

        for selector in selectors:
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text = element.text.strip()

                if text:
                    price_text = text
                    break
            except:
                continue

        if not price_text:
            print("Selenium: Price element not found")
            return None

        # 🔢 Clean price text (₹, commas, etc.)
        price = re.sub(r"[^\d]", "", price_text)

        if price:
            return float(price)

    except Exception as e:
        print("Selenium error:", e)

    finally:
        driver.quit()

    return None
