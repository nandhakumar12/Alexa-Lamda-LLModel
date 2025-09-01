import requests
import json
import boto3

# Get the current function URL
lambda_client = boto3.client('lambda', region_name='us-east-1')

try:
    url_config = lambda_client.get_function_url_config(FunctionName='voice-assistant-llm-chatbot')
    url = url_config['FunctionUrl']
    print(f"Testing Function URL: {url}")
    print(f"Auth Type: {url_config['AuthType']}")
    
    # Test payload
    payload = {
        'message': 'Hello! Test the LLM function URL',
        'user_id': 'test-user',
        'conversation_id': 'test-url-final'
    }
    
    print(f"\nSending payload: {json.dumps(payload, indent=2)}")
    
    # Test the function URL
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ Success! LLM Response: {data.get('message', 'No message')}")
            print(f"✅ Model: {data.get('model', 'Unknown')}")
        except:
            print(f"✅ Success but couldn't parse JSON: {response.text}")
    else:
        print(f"❌ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
