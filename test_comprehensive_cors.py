#!/usr/bin/env python3
"""
Comprehensive CORS test script
"""
import requests
import json
import time

def test_backend_cors():
    """Test backend CORS directly"""
    print("🔧 Testing Backend CORS Directly...")
    print("=" * 50)
    
    url = "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app/api/v1/robot/interact"
    origin = "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app"
    
    # Test 1: OPTIONS preflight request
    print("\n1️⃣ Testing OPTIONS preflight request...")
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(url, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        missing_headers = [h for h in cors_headers if h not in response.headers]
        
        if response.status_code == 200 and not missing_headers:
            print("   ✅ OPTIONS request successful with all CORS headers!")
            print(f"   Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            print(f"   Methods: {response.headers.get('Access-Control-Allow-Methods')}")
            print(f"   Headers: {response.headers.get('Access-Control-Allow-Headers')}")
        else:
            print(f"   ❌ OPTIONS request failed or missing headers: {missing_headers}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: POST request with CORS headers
    print("\n2️⃣ Testing POST request with CORS headers...")
    headers = {
        "Origin": origin,
        "Content-Type": "application/json"
    }
    
    data = {
        "user_message": "Hello"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ POST request successful!")
            print(f"   Response: {response.json()}")
            
            if "Access-Control-Allow-Origin" in response.headers:
                print("   ✅ CORS headers present in response!")
            else:
                print("   ⚠️  CORS headers missing in response")
        else:
            print(f"   ❌ POST request failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_frontend_proxy():
    """Test frontend proxy (simulated)"""
    print("\n🌐 Testing Frontend Proxy (Simulated)...")
    print("=" * 50)
    
    # Simulate what the frontend would do with relative URLs
    frontend_url = "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app"
    backend_url = "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app"
    
    print(f"Frontend URL: {frontend_url}")
    print(f"Backend URL: {backend_url}")
    print("With Vercel proxy, frontend requests to /api/* will be proxied to backend")
    
    # Test the proxy endpoint
    proxy_url = f"{frontend_url}/api/v1/robot/interact"
    print(f"\nTesting proxy endpoint: {proxy_url}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "user_message": "Test via proxy"
    }
    
    try:
        response = requests.post(proxy_url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Proxy request successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Proxy request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_curl_command():
    """Test the curl command provided by user"""
    print("\n🐚 Testing Curl Command...")
    print("=" * 50)
    
    print("Curl command to test:")
    curl_cmd = '''curl -X POST https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app/api/v1/robot/interact \\
  -H "Content-Type: application/json" \\
  -H "Origin: https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app" \\
  -d '{"user_message": "Hello"}'
'''
    print(curl_cmd)
    
    # Simulate the curl request
    url = "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app/api/v1/robot/interact"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app"
    }
    data = {"user_message": "Hello"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Curl simulation successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Curl simulation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Comprehensive CORS Test Suite")
    print("=" * 60)
    
    test_backend_cors()
    test_frontend_proxy()
    test_curl_command()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("1. Backend CORS: Check if OPTIONS and POST requests work")
    print("2. Frontend Proxy: Check if Vercel proxy configuration works")
    print("3. Curl Test: Verify the exact command provided by user")
    print("\n💡 Next Steps:")
    print("- Deploy the backend CORS fix")
    print("- Deploy the frontend proxy configuration")
    print("- Test the actual frontend application")

if __name__ == "__main__":
    main() 