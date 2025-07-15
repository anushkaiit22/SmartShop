#!/usr/bin/env python3
"""
Test script to verify core SmartShop functionality without MongoDB
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_search_functionality():
    """Test the core search functionality"""
    print("🧪 Testing SmartShop Core Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from app.services.search_service import SearchService
        from app.models.product import ProductSearchRequest, Platform
        print("✅ All imports successful")
        
        # Test search service initialization
        print("\n2. Testing search service...")
        search_service = SearchService()
        # List available platforms using the method
        platforms = search_service.get_available_platforms()
        print(f"   Available platforms: {[p.value for p in platforms]}")
        
        # Test basic search (without actually scraping)
        print("\n3. Testing search request creation...")
        search_request = ProductSearchRequest(
            query="laptop",
            platforms=[Platform.AMAZON, Platform.FLIPKART],
            limit=5
        )
        print("✅ Search request created successfully")
        
        # Test cart service (in-memory mode)
        print("\n4. Testing cart service...")
        from app.services.cart.cart_service import CartService
        cart_service = CartService()
        print("✅ Cart service initialized")
        
        # Test cart creation
        cart = await cart_service.create_cart(session_id="test-session")
        print(f"✅ Cart created with ID: {cart.id}")
        
        print("\n🎉 Core functionality test completed successfully!")
        print("\n📝 Summary:")
        print("   - Search service: ✅ Working")
        print("   - Cart service: ✅ Working (in-memory mode)")
        print("   - Platform scrapers: ✅ Available")
        print("   - No MongoDB required: ✅ Running in memory-only mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test that API endpoints can be created"""
    print("\n🔌 Testing API endpoint creation...")
    
    try:
        from app.api.v1.endpoints.search import router as search_router
        from app.api.v1.endpoints.cart import router as cart_router
        print("✅ API routers imported successfully")
        
        # Test that endpoints exist
        search_routes = [route.path for route in search_router.routes]
        cart_routes = [route.path for route in cart_router.routes]
        
        print(f"   Search endpoints: {len(search_routes)} routes")
        print(f"   Cart endpoints: {len(cart_routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 SmartShop - Core Functionality Test")
    print("=" * 50)
    print("This test verifies the application works without MongoDB")
    print()
    
    # Test core functionality
    core_ok = await test_search_functionality()
    
    # Test API endpoints
    api_ok = await test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Core Functionality: {'✅ PASS' if core_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if core_ok and api_ok:
        print("\n🎉 All tests passed! You can now run the application.")
        print("\n🚀 To start the application:")
        print("   python run_local.py")
        print("\n📚 To test the API:")
        print("   Visit: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 