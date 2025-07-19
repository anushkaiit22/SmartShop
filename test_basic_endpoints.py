#!/usr/bin/env python3
"""
Test basic endpoints to check if the API is accessible
"""

import requests
import json

def test_basic_endpoints():
    """Test basic endpoints"""
    base_url = "https://smartshop-backend-rb36f2zok-anushka-pimpales-projects.vercel.app"
    
    endpoints_to_test = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/docs", "API documentation"),
        ("/api/v1/search/?q=test&limit=5", "Search endpoint")
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"\nTesting {description}: {base_url}{endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                if endpoint == "/":
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
            elif response.status_code == 401:
                print("❌ Authentication required - This endpoint is protected")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_basic_endpoints() 