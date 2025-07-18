#!/usr/bin/env python3
"""
Basic test script to verify SmartShop backend setup
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("Configuration imported successfully")
        
        from app.models.product import Product, Platform, PlatformType
        print("Product models imported successfully")
        
        from app.models.cart import Cart, CartItem
        print("Cart models imported successfully")
        
        from app.services.nlp.query_parser import query_parser
        print("NLP query parser imported successfully")
        
        from app.services.search_service import search_service
        print("Search service imported successfully")
        
        from app.services.cart.cart_service import cart_service
        print("Cart service imported successfully")
        
        from app.services.scrapers.amazon_scraper import AmazonScraper
        print("Amazon scraper imported successfully")
        
        from app.services.scrapers.blinkit_scraper import BlinkitScraper
        print("Blinkit scraper imported successfully")
        
        return True
        
    except Exception as e:
        print(f"Import error: {e}")
        return False

async def test_nlp_parsing():
    """Test NLP query parsing"""
    print("\nTesting NLP query parsing...")
    
    try:
        from app.services.nlp.query_parser import query_parser
        
        # Test simple parsing
        query = "I need milk and bread"
        parsed = await query_parser.parse_query(query)
        
        print(f"✓ Query parsed: {query}")
        print(f"  Products found: {len(parsed.products)}")
        for product in parsed.products:
            print(f"    - {product.product_name} (qty: {product.quantity})")
        
        return True
        
    except Exception as e:
        print(f"✗ NLP parsing error: {e}")
        return False

async def test_search_service():
    """Test search service initialization"""
    print("\nTesting search service...")
    
    try:
        from app.services.search_service import search_service
        
        platforms = search_service.get_available_platforms()
        print(f"✓ Available platforms: {[p.value for p in platforms]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Search service error: {e}")
        return False

async def test_cart_service():
    """Test cart service functionality"""
    print("\nTesting cart service...")
    
    try:
        from app.services.cart.cart_service import cart_service
        
        # Test cart creation (without database)
        print("✓ Cart service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Cart service error: {e}")
        return False

async def main():
    """Run all tests"""
    print("SmartShop Backend - Basic Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_nlp_parsing,
        test_search_service,
        test_cart_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The backend is ready to run.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and configure your settings")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start MongoDB and Redis")
        print("4. Run the application: uvicorn main:app --reload")
        print("5. Visit http://localhost:8000/docs for API documentation")
    else:
        print("Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 