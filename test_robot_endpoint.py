#!/usr/bin/env python3
"""
Test script for the robot endpoint
"""

import requests
import json

def test_robot_endpoint():
    """Test the robot endpoint"""
    base_url = "https://smartshop-backend-rb36f2zok-anushka-pimpales-projects.vercel.app"
    endpoint = "/api/v1/robot/interact"
    
    print(f"Testing robot endpoint: {base_url}{endpoint}")
    
    # Test data
    test_data = {
        "user_message": "Hello",
        "cart_id": None,
        "last_action": None,
        "platforms": ["flipkart"]
    }
    
    try:
        print(f"Sending POST request to: {base_url}{endpoint}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            print("✅ Robot endpoint is working!")
        else:
            print(f"❌ Robot endpoint failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_robot_endpoint() 