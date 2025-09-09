#!/usr/bin/env python3
"""
Test script for Voice Assistant AI API endpoints
"""

import requests
import json
import time

# API Gateway base URL
BASE_URL = "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/v1"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS")
            return True
        else:
            print("   ❌ FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Test all API endpoints"""
    print("🚀 Testing Voice Assistant AI API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint")
    test_endpoint("GET", "/health")
    
    # Test auth endpoint
    print("\n2. Testing Auth Endpoint")
    test_endpoint("POST", "/auth", {"action": "health_check"})
    
    # Test chatbot endpoint (should be unauthorized)
    print("\n3. Testing Chatbot Endpoint (should be unauthorized)")
    test_endpoint("POST", "/chatbot", {"message": "hello"})
    
    # Test alexa endpoint
    print("\n4. Testing Alexa Endpoint")
    test_endpoint("POST", "/alexa", {"version": "1.0", "request": {"type": "LaunchRequest"}})
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    main()
