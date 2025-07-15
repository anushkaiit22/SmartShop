import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import logging
from app.services.scrapers.amazon_scraper import AmazonScraper
from app.services.scrapers.flipkart_scraper import FlipkartScraper
from app.services.scrapers.blinkit_scraper import BlinkitScraper

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_amazon_scraper():
    print("Testing Amazon scraper...")
    try:
        async with AmazonScraper() as scraper:
            products = await scraper.search_products('laptop', limit=5)
            print(f"Found {len(products)} products on Amazon")
            for i, product in enumerate(products[:3]):
                print(f"{i+1}. {product.name}")
                print(f"   Price: ₹{product.price.current_price}")
                print(f"   Rating: {product.rating.rating if product.rating else 'N/A'}")
                print(f"   URL: {product.platform_url}")
                print()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def test_flipkart_scraper():
    print("Testing Flipkart scraper...")
    try:
        async with FlipkartScraper() as scraper:
            products = await scraper.search_products('laptop', limit=5)
            print(f"Found {len(products)} products on Flipkart")
            for i, product in enumerate(products[:3]):
                print(f"{i+1}. {product.name}")
                print(f"   Price: ₹{product.price.current_price}")
                print(f"   Rating: {product.rating.rating if product.rating else 'N/A'}")
                print(f"   URL: {product.platform_url}")
                print()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def test_blinkit_scraper():
    print("Testing Blinkit scraper...")
    try:
        async with BlinkitScraper() as scraper:
            products = await scraper.search_products('milk', limit=5)
            print(f"Found {len(products)} products on Blinkit")
            for i, product in enumerate(products[:3]):
                print(f"{i+1}. {product.name}")
                print(f"   Price: ₹{product.price.current_price}")
                print(f"   Rating: {product.rating.rating if product.rating else 'N/A'}")
                print(f"   URL: {product.platform_url}")
                print()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_amazon_scraper()
    await test_flipkart_scraper()
    await test_blinkit_scraper()

if __name__ == "__main__":
    asyncio.run(main()) 