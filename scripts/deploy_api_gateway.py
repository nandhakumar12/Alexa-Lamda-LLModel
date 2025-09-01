import boto3
import json
import requests

# Initialize AWS clients
apigateway = boto3.client('apigateway', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

function_name = 'voice-assistant-llm-chatbot'

try:
    # Get the Lambda function ARN
    function_response = lambda_client.get_function(FunctionName=function_name)
    function_arn = function_response['Configuration']['FunctionArn']
    print(f"Lambda Function ARN: {function_arn}")
    
    # Check if API Gateway exists
    apis = apigateway.get_rest_apis()
    llm_api = None
    
    for api in apis['items']:
        if api['name'] == 'voice-assistant-llm-api':
            llm_api = api
            break
    
    if llm_api:
        api_id = llm_api['id']
        print(f"Found existing API Gateway: {api_id}")
        
        # Test the API Gateway endpoint
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chat"
        print(f"Testing API Gateway URL: {api_url}")
        
        payload = {
            'message': 'Hello! Test API Gateway endpoint',
            'user_id': 'test-user',
            'conversation_id': 'test-api-gateway'
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ API Gateway working! LLM Response: {data.get('message', 'No message')[:100]}...")
                    
                    # Update the frontend with the working endpoint
                    print(f"\n🎉 Working API Gateway endpoint: {api_url}")
                    print("✅ This endpoint should be used in the frontend")
                    
                except:
                    print(f"✅ API Gateway working: {response.text[:100]}...")
            else:
                print(f"❌ API Gateway error: {response.text}")
                
        except Exception as e:
            print(f"❌ API Gateway test error: {e}")
    else:
        print("❌ No API Gateway found. Need to deploy via Terraform.")
        print("Run: cd infra/terraform && terraform apply")
        
except Exception as e:
    print(f"❌ Error: {e}")
