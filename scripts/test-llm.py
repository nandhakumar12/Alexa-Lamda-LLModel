#!/usr/bin/env python3

"""
Test script for LLM-powered Voice Assistant
Tests both Lambda function and API Gateway endpoints
"""

import json
import boto3
import requests
import time
from datetime import datetime

def test_lambda_function():
    """Test the Lambda function directly"""
    print("🧪 Testing Lambda function directly...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        test_payload = {
            "body": json.dumps({
                "message": "Hello, can you help me with music?",
                "user_id": "test-user",
                "conversation_id": f"test-{int(time.time())}"
            })
        }
        
        response = lambda_client.invoke(
            FunctionName='voice-assistant-llm-chatbot',
            Payload=json.dumps(test_payload)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✅ Lambda test successful!")
        print(f"📝 Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        return False

def test_api_gateway():
    """Test the API Gateway endpoint"""
    print("\n🌐 Testing API Gateway endpoint...")
    
    # Try different possible endpoints
    endpoints = [
        'https://bnemssy6o6llk2fgijrnuynk7e0vpnnj.lambda-url.us-east-1.on.aws/',
        'https://jv3ikn4o1m.execute-api.us-east-1.amazonaws.com/prod/chat',
        'https://7orgj957oe.execute-api.us-east-1.amazonaws.com/prod/chat',
        'https://7orgj957oe.execute-api.us-east-1.amazonaws.com/v1/chat'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Trying endpoint: {endpoint}")
            
            payload = {
                "message": "Hello, I'm testing the LLM integration",
                "user_id": "test-user",
                "conversation_id": f"test-{int(time.time())}"
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Gateway test successful!")
                print(f"📝 Response: {result}")
                return True
            else:
                print(f"⚠️ Status code: {response.status_code}")
                print(f"📝 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ API test failed for {endpoint}: {e}")
    
    return False

def test_bedrock_access():
    """Test Bedrock model access"""
    print("\n🧠 Testing Bedrock model access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test. Please respond briefly."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        print(f"✅ Bedrock test successful!")
        print(f"📝 Claude response: {response_body['content'][0]['text']}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock test failed: {e}")
        return False

def test_dynamodb_access():
    """Test DynamoDB table access"""
    print("\n🗄️ Testing DynamoDB access...")
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('voice-assistant-conversations')
        
        # Test write
        test_item = {
            'user_id': 'test-user',
            'sort_key': f'test-{int(time.time())}#user',
            'conversation_id': 'test-conversation',
            'message': 'Test message',
            'message_type': 'user',
            'timestamp': datetime.now().isoformat()
        }
        
        table.put_item(Item=test_item)
        print(f"✅ DynamoDB write test successful!")
        
        # Test read
        response = table.get_item(
            Key={
                'user_id': 'test-user',
                'sort_key': test_item['sort_key']
            }
        )
        
        if 'Item' in response:
            print(f"✅ DynamoDB read test successful!")
            return True
        else:
            print(f"⚠️ Item not found in DynamoDB")
            return False
            
    except Exception as e:
        print(f"❌ DynamoDB test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LLM Voice Assistant - Infrastructure Test Suite")
    print("=" * 60)
    
    tests = [
        ("Bedrock Model Access", test_bedrock_access),
        ("DynamoDB Access", test_dynamodb_access),
        ("Lambda Function", test_lambda_function),
        ("API Gateway", test_api_gateway)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! LLM infrastructure is ready!")
        print("💰 Estimated cost: $1-5/month for light usage")
        print("🧠 Claude Haiku model is 90% cheaper than GPT-4")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
        print("💡 Make sure AWS credentials are configured and Bedrock access is enabled.")
    
    print("\n🔗 Next steps:")
    print("1. Visit your Voice Assistant web app")
    print("2. Toggle 'LLM Mode' ON in the interface")
    print("3. Try natural conversations with Claude Haiku")
    print("4. Monitor costs with: python scripts/monitor-llm-costs.py")

if __name__ == "__main__":
    main()
