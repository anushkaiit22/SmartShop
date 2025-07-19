#!/usr/bin/env python3
"""
Test script to verify CORS configuration
"""
import requests
import json

def test_cors_preflight():
    """Test CORS preflight request"""
    url = "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app/api/v1/robot/interact"
    
    headers = {
        "Origin": "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    print("Testing CORS preflight request...")
    try:
        response = requests.options(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Check for CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        missing_headers = [h for h in cors_headers if h not in response.headers]
        
        if not missing_headers:
            print("✅ All CORS headers found!")
            print(f"Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            print(f"Methods: {response.headers.get('Access-Control-Allow-Methods')}")
            print(f"Headers: {response.headers.get('Access-Control-Allow-Headers')}")
        else:
            print(f"❌ Missing CORS headers: {missing_headers}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_robot_endpoint():
    """Test the robot endpoint"""
    url = "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app/api/v1/robot/interact"
    
    headers = {
        "Origin": "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app",
        "Content-Type": "application/json"
    }
    
    data = {
        "user_message": "Hello"
    }
    
    print("\nTesting robot endpoint...")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cors_preflight()
    test_robot_endpoint() 