#!/usr/bin/env python3
"""
Simple API Gateway fix - create a clean working endpoint
"""

import boto3
import json
import time

# Initialize AWS clients
apigateway = boto3.client('apigateway', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def main():
    print("🔧 Creating clean API Gateway setup...")
    
    account_id = get_account_id()
    print(f"📋 Account ID: {account_id}")
    
    # Step 1: Find the Lambda function
    function_name = 'voice-assistant-ai-prod-chatbot'
    function_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:{function_name}"
    
    try:
        lambda_client.get_function(FunctionName=function_name)
        print(f"✅ Found Lambda function: {function_name}")
    except Exception as e:
        print(f"❌ Lambda function not found: {e}")
        return
    
    # Step 2: Delete existing API Gateway if it exists
    try:
        apis = apigateway.get_rest_apis()
        for api in apis['items']:
            if api['name'] == 'voice-assistant-clean-api':
                print(f"🗑️  Deleting existing API: {api['id']}")
                apigateway.delete_rest_api(restApiId=api['id'])
                time.sleep(2)
    except Exception as e:
        print(f"⚠️  Warning cleaning up: {e}")
    
    # Step 3: Create new API Gateway
    try:
        api = apigateway.create_rest_api(
            name='voice-assistant-clean-api',
            description='Clean Voice Assistant API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api['id']
        print(f"✅ Created API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create chatbot resource
        chatbot_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='chatbot'
        )
        chatbot_id = chatbot_resource['id']
        print(f"✅ Created /chatbot resource: {chatbot_id}")
        
        # Create POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        print("✅ Created POST method")
        
        # Create Lambda integration
        lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        print("✅ Created Lambda integration")
        
        # Grant permission to API Gateway
        try:
            source_arn = f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
            
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'apigateway-{api_id}-{int(time.time())}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=source_arn
            )
            print("✅ Granted Lambda permission")
        except Exception as e:
            if "ResourceConflictException" not in str(e):
                print(f"⚠️  Permission warning: {e}")
        
        # Deploy API
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        print("✅ Deployed API to prod stage")
        
        endpoint_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"🌐 API Endpoint: {endpoint_url}/chatbot")
        
        # Test the endpoint
        print("\n🧪 Testing endpoint...")
        import requests
        
        test_data = {
            "message": "Hello! Can you help me?",
            "user_id": "test-user"
        }
        
        try:
            response = requests.post(
                f"{endpoint_url}/chatbot",
                json=test_data,
                timeout=15
            )
            
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result.get('response', 'No response')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
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
            print(f"📝 Please manually update frontend/.env with:")
            print(f"   REACT_APP_API_GATEWAY_URL={endpoint_url}")
        
        return endpoint_url
        
    except Exception as e:
        print(f"❌ Error creating API: {e}")
        return None

if __name__ == "__main__":
    main()
