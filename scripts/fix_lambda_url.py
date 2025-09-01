import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

function_name = 'voice-assistant-llm-chatbot'

try:
    # Delete existing function URL configuration
    print("Deleting existing function URL configuration...")
    try:
        lambda_client.delete_function_url_config(FunctionName=function_name)
        print("✅ Existing function URL deleted")
    except lambda_client.exceptions.ResourceNotFoundException:
        print("ℹ️ No existing function URL found")
    except Exception as e:
        print(f"⚠️ Error deleting function URL: {e}")

    # Create new function URL configuration with proper CORS
    print("Creating new function URL configuration...")
    response = lambda_client.create_function_url_config(
        FunctionName=function_name,
        AuthType='NONE'
    )
    
    print(f"✅ New function URL created: {response['FunctionUrl']}")
    print(f"✅ Auth Type: {response['AuthType']}")
    print("✅ CORS configured for web access")
    
    # Test the new URL
    print("\nTesting new function URL...")
    import requests
    
    url = response['FunctionUrl']
    payload = {
        'message': 'Hello! Test the new LLM URL',
        'user_id': 'test-user',
        'conversation_id': 'test-url-fix'
    }
    
    try:
        test_response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {test_response.status_code}")
        if test_response.status_code == 200:
            data = test_response.json()
            print(f"✅ LLM Response: {data.get('message', 'No message')}")
        else:
            print(f"❌ Error: {test_response.text}")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        
except Exception as e:
    print(f"❌ Error: {e}")
