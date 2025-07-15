import sys
import os
import asyncio

# Ensure app imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.scrapers.flipkart_scraper import FlipkartScraper
from app.services.scrapers.meesho_scraper import MeeshoScraper

async def test_non_playwright_scrapers():
    print("\n=== Non-Playwright Scrapers ===")
    # Test Flipkart (Amazon and Blinkit are blocked by anti-bot protection)
    try:
        async with FlipkartScraper() as scraper:
            products = await scraper.search_products('laptop', limit=3)
            print(f"Flipkart (requests/bs4): Found {len(products)} products")
            for p in products:
                print(f"- {p.name} | ₹{p.price.current_price} | {p.platform_url}")
    except Exception as e:
        print(f"Flipkart scraper error: {e}")
    
    # Test Meesho (requests/bs4)
    try:
        async with MeeshoScraper() as scraper:
            products = await scraper.search_products('laptop', limit=3)
            print(f"Meesho (requests/bs4): Found {len(products)} products")
            for p in products:
                print(f"- {p.name} | ₹{p.price.current_price} | {p.platform_url}")
    except Exception as e:
        print(f"Meesho scraper error: {e}")

if __name__ == "__main__":
    asyncio.run(test_non_playwright_scrapers()) 