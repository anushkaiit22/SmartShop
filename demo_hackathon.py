import asyncio
import json
from app.services.search_service import search_service
from app.models.product import ProductSearchRequest, Platform

async def demo_price_comparison():
    """Demo script for hackathon presentation"""
    print("SmartShop Price Comparison Demo")
    print("=" * 50)
    
    # Demo queries
    queries = [
        "laptop under 50000",
        "smartphone with 4+ rating",
        "milk and bread",
        "gaming mouse"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        print("-" * 30)
        
        # Create search request
        request = ProductSearchRequest(
            query=query,
            platforms=[Platform.AMAZON, Platform.FLIPKART, Platform.MEESHO, Platform.BLINKIT],
            limit=8
        )
        
        # Perform search
        response = await search_service.search_products(request)
        
        if response.success and response.data:
            products = response.data.products
            
            # Group by platform
            platform_products = {}
            for product in products:
                platform = product.platform.value
                if platform not in platform_products:
                    platform_products[platform] = []
                platform_products[platform].append(product)
            
            # Display results by platform
            for platform, platform_prods in platform_products.items():
                print(f"\n{platform.upper()}:")
                for i, product in enumerate(platform_prods[:3], 1):
                    rating_text = f"{product.rating.rating}" if product.rating else "No rating"
                    delivery_text = f"{product.delivery.delivery_time}"
                    print(f"  {i}. {product.name[:40]}...")
                    print(f"     ₹{product.price.current_price} | {rating_text} | {delivery_text}")
            
            print(f"\n  Search completed in {response.data.search_time:.2f} seconds")
            print(f"  Total results: {response.data.total_results}")
            
        else:
            print(f"❌ Search failed: {response.error}")
        
        print("\n" + "=" * 50)

async def demo_natural_language():
    """Demo natural language processing"""
    print("\nNatural Language Processing Demo")
    print("=" * 50)
    
    natural_queries = [
        "I need a laptop for gaming under 60000",
        "Find me a smartphone with good camera and 4+ rating",
        "Looking for groceries: milk, bread, and eggs"
    ]
    
    for query in natural_queries:
        print(f"\nQuery: '{query}'")
        
        request = ProductSearchRequest(
            query=query,
            limit=5
        )
        
        response = await search_service.search_products(request)
        
        if response.success and response.data:
            print(f"Found {len(response.data.products)} products")
            print(f"Parsed message: {response.message}")
        else:
            print(f"❌ Failed: {response.error}")

async def demo_platform_comparison():
    """Demo comparing specific platforms"""
    print("\nPlatform Comparison Demo")
    print("=" * 50)
    
    # Compare e-commerce vs quick commerce
    print("\nE-commerce (Amazon, Flipkart, Meesho):")
    request = ProductSearchRequest(
        query="laptop",
        platforms=[Platform.AMAZON, Platform.FLIPKART, Platform.MEESHO],
        limit=6
    )
    response = await search_service.search_products(request)
    if response.success:
        for product in response.data.products[:3]:
            print(f"  • {product.platform.value}: ₹{product.price.current_price} | {product.delivery.delivery_time}")
    
    print("\nQuick Commerce (Blinkit):")
    request = ProductSearchRequest(
        query="milk",
        platforms=[Platform.BLINKIT],
        limit=3
    )
    response = await search_service.search_products(request)
    if response.success:
        for product in response.data.products:
            print(f"  • {product.platform.value}: ₹{product.price.current_price} | {product.delivery.delivery_time}")

def main():
    """Run all demos"""
    print("SmartShop - Unified Shopping Assistant")
    print("Compare prices across Amazon, Flipkart, Meesho, and Blinkit")
    print("Features: Real-time search, Natural language processing, Price comparison")
    print("\n" + "=" * 60)
    
    asyncio.run(demo_price_comparison())
    asyncio.run(demo_natural_language())
    asyncio.run(demo_platform_comparison())
    
    print("\nDemo completed!")
    print("\nFor Hackathon Judges:")
    print("Real Flipkart integration (live data)")
    print("Mock data for other platforms (realistic)")
    print("Natural language processing")
    print("Multi-platform price comparison")
    print("Fast API responses")
    print("Production-ready architecture")

if __name__ == "__main__":
    main() 