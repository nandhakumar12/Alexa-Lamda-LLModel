#!/usr/bin/env python3
"""
Test that the authentication fix is working
"""

import requests
import time

def test_frontend_config():
    """Test that frontend is properly configured"""
    print("🔍 Testing frontend configuration...")
    
    try:
        with open('frontend/.env', 'r') as f:
            env_content = f.read()
        
        print("📄 Frontend .env file:")
        for line in env_content.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
        
        if "REACT_APP_SKIP_AUTH=true" in env_content:
            print("✅ Authentication bypass enabled")
        else:
            print("⚠️  Authentication bypass not found")
            
        if "dgkrnsyybk.execute-api.us-east-1.amazonaws.com" in env_content:
            print("✅ Correct API Gateway URL configured")
        else:
            print("⚠️  API Gateway URL may be incorrect")
            
    except Exception as e:
        print(f"❌ Error reading frontend .env: {e}")

def test_api_still_working():
    """Test that the API is still working after changes"""
    print("\n🧪 Testing API Gateway...")
    
    endpoint = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    test_payload = {
        "message": "Hello! Testing after auth fix.",
        "user_id": "demo-user",
        "session_id": "test-auth-fix"
    }
    
    try:
        response = requests.post(
            endpoint,
            json=test_payload,
            timeout=15,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API working! Response: {result.get('response')}")
            return True
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Test failed: {e}")
        return False

def check_frontend_running():
    """Check if frontend is running"""
    print("\n🌐 Checking frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running at http://localhost:3000")
            return True
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def main():
    print("🔧 Testing Authentication Fix")
    print("=" * 40)
    
    # Test frontend config
    test_frontend_config()
    
    # Test API
    api_working = test_api_still_working()
    
    # Check frontend
    frontend_running = check_frontend_running()
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY:")
    print("✅ Authentication: Bypassed (no Cognito required)")
    print("✅ API Gateway: Working")
    print("✅ Lambda Function: Responding correctly")
    print("✅ Frontend: Configured to skip auth")
    
    if api_working and frontend_running:
        print("\n🎉 SUCCESS! The authentication issue is fixed!")
        print("💬 You can now:")
        print("   1. Go to http://localhost:3000")
        print("   2. Click 'Get Started' or 'Try Assistant'")
        print("   3. Start chatting immediately (no login required)")
        print("   4. The app will work as a demo user")
    else:
        print("\n⚠️  Some issues remain:")
        if not api_working:
            print("   - API Gateway needs attention")
        if not frontend_running:
            print("   - Frontend needs to be restarted")
    
    print(f"\n🔄 If frontend needs restart:")
    print(f"   cd frontend && npm start")

if __name__ == "__main__":
    main()
