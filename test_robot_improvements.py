#!/usr/bin/env python3
"""
Test script to verify robot improvements with fallbacks and timeouts
"""

import asyncio
import time
import requests
import json

def test_robot_endpoint():
    """Test the robot endpoint with various scenarios"""
    
    base_url = "http://localhost:8000"  # Change to your deployed URL if testing production
    
    test_cases = [
        {
            "name": "Basic product search",
            "data": {
                "user_message": "amul cheese",
                "platforms": ["flipkart"]
            }
        },
        {
            "name": "Search with timeout simulation",
            "data": {
                "user_message": "very specific product that might not exist",
                "platforms": ["flipkart"]
            }
        },
        {
            "name": "Natural language query",
            "data": {
                "user_message": "I need to buy some milk",
                "platforms": ["flipkart"]
            }
        },
        {
            "name": "Product selection",
            "data": {
                "user_message": "add laptop to cart",
                "platforms": ["flipkart"]
            }
        }
    ]
    
    print("🤖 Testing Robot Endpoint Improvements")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/v1/robot/interact",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=20  # 20 second timeout for the entire request
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                print(f"🎯 Action: {data.get('action', 'unknown')}")
                print(f"💬 Message: {data.get('message', 'No message')}")
                
                if data.get('data'):
                    products = data['data']
                    if isinstance(products, list):
                        print(f"📦 Products found: {len(products)}")
                        for j, product in enumerate(products[:3], 1):  # Show first 3
                            name = product.get('name', product.get('product_name', 'Unknown'))
                            price = product.get('price', {}).get('current_price', 'N/A')
                            platform = product.get('platform', 'Unknown')
                            print(f"   {j}. {name} - ₹{price} ({platform})")
                    else:
                        print(f"📦 Data: {type(products)}")
                
                if data.get('cart_id'):
                    print(f"🛒 Cart ID: {data['cart_id']}")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - make sure the server is running")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
        
        print()

def test_search_service():
    """Test the search service directly"""
    
    base_url = "http://localhost:8000"
    
    search_queries = [
        "amul cheese",
        "laptop",
        "mobile phone",
        "nonexistent product xyz123"
    ]
    
    print("🔍 Testing Search Service with Fallbacks")
    print("=" * 50)
    
    for query in search_queries:
        print(f"\n🔎 Searching for: '{query}'")
        print("-" * 30)
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{base_url}/api/v1/search/",
                params={
                    "q": query,
                    "limit": 5,
                    "platforms": "flipkart"
                },
                timeout=15
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                print(f"💬 Message: {data.get('message', 'No message')}")
                
                if data.get('data', {}).get('products'):
                    products = data['data']['products']
                    print(f"📦 Products found: {len(products)}")
                    
                    for i, product in enumerate(products[:3], 1):
                        name = product.get('name', product.get('product_name', 'Unknown'))
                        price = product.get('price', {}).get('current_price', 'N/A')
                        platform = product.get('platform', 'Unknown')
                        print(f"   {i}. {name} - ₹{price} ({platform})")
                else:
                    print("📦 No products found")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
        
        print()

def test_configuration():
    """Test if configuration changes are applied"""
    
    base_url = "http://localhost:8000"
    
    print("⚙️  Testing Configuration Changes")
    print("=" * 50)
    
    try:
        # Test a simple endpoint to check if server is running
        response = requests.get(f"{base_url}/api/v1/search/", params={"q": "test"}, timeout=5)
        
        if response.status_code == 200:
            print("✅ Server is running and responding")
            
            # Test timeout behavior
            print("\n⏱️  Testing timeout behavior...")
            start_time = time.time()
            
            response = requests.get(
                f"{base_url}/api/v1/search/",
                params={"q": "very specific product that might cause timeout"},
                timeout=12  # Should be less than scraper timeout + buffer
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            
            if response_time < 12:
                print("✅ Response within expected timeout")
            else:
                print("⚠️  Response took longer than expected")
                
        else:
            print(f"❌ Server responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Cannot connect to server - make sure it's running")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Robot Improvements Test Suite")
    print("=" * 60)
    
    # Test configuration first
    test_configuration()
    
    # Test search service
    test_search_service()
    
    # Test robot endpoint
    test_robot_endpoint()
    
    print("\n🎉 Test suite completed!")
    print("\n📋 Summary:")
    print("- Reduced timeouts for better Vercel performance")
    print("- Added comprehensive fallback mechanisms")
    print("- Improved error handling and user feedback")
    print("- Added mock data fallbacks when real scrapers fail")
    print("- Enhanced frontend with loading states and retry buttons") 