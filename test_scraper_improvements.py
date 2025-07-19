#!/usr/bin/env python3
"""
Test script to verify scraper improvements
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.scrapers.flipkart_scraper import FlipkartScraper
from app.services.search_service import SearchService
from app.models.product import ProductSearchRequest, Platform

async def test_scraper_improvements():
    """Test the scraper improvements"""
    print("Testing scraper improvements...")
    
    # Test Flipkart scraper directly
    print("\n1. Testing Flipkart scraper directly...")
    try:
        async with FlipkartScraper() as scraper:
            products = await scraper.search_products("milk", limit=3)
            print(f"Found {len(products)} products from Flipkart")
            for product in products:
                print(f"  - {product.name}: ₹{product.price.current_price}")
    except Exception as e:
        print(f"Flipkart scraper error: {e}")
    
    # Test search service
    print("\n2. Testing search service...")
    try:
        search_service = SearchService()
        request = ProductSearchRequest(
            query="milk",
            limit=5,
            platforms=[Platform.FLIPKART, Platform.AMAZON]
        )
        response = await search_service.search_products(request)
        print(f"Search service response: {response.success}")
        if response.success:
            print(f"Found {len(response.data.products)} total products")
            for product in response.data.products:
                print(f"  - {product.name} ({product.platform.value}): ₹{product.price.current_price}")
    except Exception as e:
        print(f"Search service error: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper_improvements()) 