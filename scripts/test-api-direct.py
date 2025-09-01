#!/usr/bin/env python3
"""
Test the API Gateway directly to debug issues
"""

import requests
import json

def test_api_gateway():
    """Test API Gateway directly"""
    print("🧪 Testing API Gateway directly...")
    
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    # Test payload
    test_payload = {
        "message": "Hello! This is a direct API test.",
        "type": "text",
        "session_id": "direct-test-user"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    }
    
    try:
        print(f"📤 Sending request to: {api_url}")
        print(f"📋 Payload: {json.dumps(test_payload, indent=2)}")
        
        response = requests.post(
            api_url, 
            json=test_payload, 
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n🔍 Testing CORS preflight...")
    
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    headers = {
        "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(api_url, headers=headers, timeout=10)
        print(f"📊 CORS Preflight Status: {response.status_code}")
        print(f"📋 CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
        else:
            print("❌ CORS preflight failed")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")

def test_lambda_direct():
    """Test Lambda function directly using boto3"""
    print("\n⚡ Testing Lambda function directly...")
    
    try:
        import boto3
        
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        test_event = {
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Hello! Direct Lambda test.",
                "type": "text",
                "session_id": "lambda-direct-test"
            })
        }
        
        response = lambda_client.invoke(
            FunctionName='voice-assistant-ai-prod-chatbot',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✅ Lambda Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Lambda test error: {e}")

def main():
    print("🔧 API Debugging Tool")
    print("=" * 50)
    
    # Test 1: Direct API Gateway
    test_api_gateway()
    
    # Test 2: CORS preflight
    test_cors_preflight()
    
    # Test 3: Direct Lambda
    test_lambda_direct()
    
    print("\n" + "=" * 50)
    print("🔍 Debugging complete!")
    print("\n💡 Common issues:")
    print("   • CORS configuration")
    print("   • Authentication headers")
    print("   • Request timeout")
    print("   • Lambda function errors")
    print("   • API Gateway configuration")

if __name__ == "__main__":
    main()
