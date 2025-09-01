#!/usr/bin/env python3
"""
Fix Lambda function handler configuration
"""

import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

def main():
    print("🔧 Fixing Lambda function handler...")
    
    function_name = 'voice-assistant-ai-prod-chatbot'
    
    try:
        # Update the function configuration to use the correct handler
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Handler='lambda_function.lambda_handler',
            Runtime='python3.9',
            Timeout=30,
            MemorySize=256
        )
        
        print(f"✅ Updated Lambda configuration:")
        print(f"   Handler: {response['Handler']}")
        print(f"   Runtime: {response['Runtime']}")
        print(f"   Timeout: {response['Timeout']}")
        print(f"   Memory: {response['MemorySize']}")
        
        # Test the function again
        print("\n🧪 Testing Lambda function...")
        
        test_event = {
            'body': json.dumps({
                'message': 'Hello! Can you help me?',
                'user_id': 'test-user'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        test_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(test_response['Payload'].read())
        print(f"📊 Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"✅ Test successful! Response: {body.get('response')}")
        else:
            print(f"❌ Test failed: {result}")
        
        # Now test the API Gateway endpoint
        print("\n🌐 Testing API Gateway endpoint...")
        import requests
        
        api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
        
        test_data = {
            "message": "Hello! Can you help me?",
            "user_id": "test-user"
        }
        
        try:
            response = requests.post(api_url, json=test_data, timeout=15)
            print(f"📊 API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Test successful! Response: {result.get('response')}")
            else:
                print(f"❌ API Error: {response.text}")
                
        except Exception as e:
            print(f"❌ API Test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda configuration: {e}")
        return False

if __name__ == "__main__":
    main()
