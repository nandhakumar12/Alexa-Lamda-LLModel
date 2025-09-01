#!/usr/bin/env python3
"""
Test the new Lambda function and update API Gateway
"""

import boto3
import json
import time
import requests

lambda_client = boto3.client('lambda', region_name='us-east-1')
apigateway = boto3.client('apigateway', region_name='us-east-1')

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def main():
    print("🧪 Testing new Lambda function...")
    
    function_name = 'voice-assistant-chatbot-fixed'
    account_id = get_account_id()
    
    # Wait for function to be ready
    print("⏳ Waiting for Lambda function to be ready...")
    for i in range(30):
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            if response['Configuration']['State'] == 'Active':
                print("✅ Lambda function is ready!")
                break
        except:
            pass
        time.sleep(2)
        print(f"   Waiting... ({i+1}/30)")
    
    # Test the Lambda function
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
    
    try:
        test_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(test_response['Payload'].read())
        print(f"📊 Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"✅ Lambda test successful! Response: {body.get('response')}")
            
            # Update API Gateway
            print("\n🔗 Updating API Gateway...")
            
            # Find the API Gateway
            apis = apigateway.get_rest_apis()
            target_api = None
            
            for api in apis['items']:
                if api['name'] == 'voice-assistant-clean-api':
                    target_api = api
                    break
            
            if target_api:
                api_id = target_api['id']
                function_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:{function_name}"
                
                # Get resources
                resources = apigateway.get_resources(restApiId=api_id)
                chatbot_resource_id = None
                
                for resource in resources['items']:
                    if resource['path'] == '/chatbot':
                        chatbot_resource_id = resource['id']
                        break
                
                if chatbot_resource_id:
                    # Update the integration to use new function
                    lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
                    
                    apigateway.put_integration(
                        restApiId=api_id,
                        resourceId=chatbot_resource_id,
                        httpMethod='POST',
                        type='AWS_PROXY',
                        integrationHttpMethod='POST',
                        uri=lambda_uri
                    )
                    
                    # Grant permission
                    source_arn = f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
                    
                    try:
                        lambda_client.add_permission(
                            FunctionName=function_name,
                            StatementId=f'apigateway-{api_id}-{int(time.time())}',
                            Action='lambda:InvokeFunction',
                            Principal='apigateway.amazonaws.com',
                            SourceArn=source_arn
                        )
                        print("✅ Granted API Gateway permission")
                    except Exception as e:
                        if "ResourceConflictException" not in str(e):
                            print(f"⚠️  Permission warning: {e}")
                    
                    # Redeploy
                    apigateway.create_deployment(
                        restApiId=api_id,
                        stageName='prod'
                    )
                    
                    endpoint_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
                    print(f"✅ Updated API Gateway: {endpoint_url}/chatbot")
                    
                    # Test the API
                    print("\n🌐 Testing API Gateway...")
                    
                    test_data = {
                        "message": "Hello! Can you help me?",
                        "user_id": "test-user"
                    }
                    
                    try:
                        response = requests.post(f"{endpoint_url}/chatbot", json=test_data, timeout=15)
                        print(f"📊 API Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"✅ API Test successful!")
                            print(f"   Response: {result.get('response')}")
                            print(f"   Session ID: {result.get('session_id')}")
                            
                            # Update frontend environment
                            env_content = f"""REACT_APP_API_GATEWAY_URL={endpoint_url}
REACT_APP_AWS_REGION=us-east-1
REACT_APP_COGNITO_USER_POOL_ID=us-east-1_TEMP
REACT_APP_COGNITO_CLIENT_ID=TEMP
"""
                            
                            try:
                                with open('frontend/.env', 'w') as f:
                                    f.write(env_content)
                                print("✅ Updated frontend/.env")
                            except Exception as e:
                                print(f"⚠️  Could not update .env: {e}")
                            
                            print(f"\n🎉 SUCCESS! Your chatbot is now working!")
                            print(f"🌐 API Endpoint: {endpoint_url}/chatbot")
                            print(f"💬 You can now refresh your frontend and test the chatbot!")
                            
                        else:
                            print(f"❌ API Error: {response.text}")
                            
                    except Exception as e:
                        print(f"❌ API Test failed: {e}")
                else:
                    print("❌ Could not find /chatbot resource")
            else:
                print("❌ Could not find API Gateway")
            
        else:
            print(f"❌ Lambda test failed: {result}")
            
    except Exception as e:
        print(f"❌ Error testing Lambda: {e}")

if __name__ == "__main__":
    main()
