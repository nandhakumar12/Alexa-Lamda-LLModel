#!/usr/bin/env python3
"""
Fix API Gateway connection to Lambda function
This script ensures the API Gateway is properly connected to the Lambda function
"""

import boto3
import json
import time

# Initialize AWS clients
apigateway = boto3.client('apigateway', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

def main():
    print("🔧 Fixing API Gateway connection...")
    
    # Step 1: Find the Lambda function
    try:
        functions = lambda_client.list_functions()
        chatbot_function = None
        
        for func in functions['Functions']:
            if 'voice-assistant' in func['FunctionName'] and 'chatbot' in func['FunctionName']:
                chatbot_function = func
                break
        
        if not chatbot_function:
            print("❌ No voice-assistant chatbot Lambda function found!")
            return
        
        function_name = chatbot_function['FunctionName']
        function_arn = chatbot_function['FunctionArn']
        print(f"✅ Found Lambda function: {function_name}")
        print(f"   ARN: {function_arn}")
        
    except Exception as e:
        print(f"❌ Error finding Lambda function: {e}")
        return
    
    # Step 2: Find or create API Gateway
    try:
        apis = apigateway.get_rest_apis()
        target_api = None
        
        for api in apis['items']:
            if 'voice-assistant' in api['name']:
                target_api = api
                break
        
        if not target_api:
            print("🆕 Creating new API Gateway...")
            target_api = apigateway.create_rest_api(
                name='voice-assistant-api',
                description='Voice Assistant API Gateway',
                endpointConfiguration={'types': ['REGIONAL']},
                binaryMediaTypes=['audio/*', 'image/*']
            )
        
        api_id = target_api['id']
        print(f"✅ Using API Gateway: {api_id}")
        
    except Exception as e:
        print(f"❌ Error with API Gateway: {e}")
        return
    
    # Step 3: Set up resources and methods
    try:
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_resource_id = None
        chatbot_resource_id = None
        
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
            elif resource['path'] == '/chatbot':
                chatbot_resource_id = resource['id']
        
        # Create /chatbot resource if it doesn't exist
        if not chatbot_resource_id:
            print("🆕 Creating /chatbot resource...")
            chatbot_resource = apigateway.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='chatbot'
            )
            chatbot_resource_id = chatbot_resource['id']
        
        print(f"✅ Chatbot resource ID: {chatbot_resource_id}")
        
        # Create OPTIONS method for CORS
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            # Add OPTIONS integration
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={'application/json': '{"statusCode": 200}'}
            )
            
            # Add OPTIONS method response
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': False,
                    'method.response.header.Access-Control-Allow-Methods': False,
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
            
            # Add OPTIONS integration response
            apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
            print("✅ OPTIONS method configured for CORS")
            
        except Exception as e:
            if "ConflictException" not in str(e):
                print(f"⚠️  Warning setting up OPTIONS: {e}")
        
        # Create POST method
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            print("✅ POST method created")
            
        except Exception as e:
            if "ConflictException" not in str(e):
                print(f"⚠️  Warning creating POST method: {e}")
        
        # Create Lambda integration
        lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        try:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            print("✅ Lambda integration configured")
            
        except Exception as e:
            print(f"⚠️  Warning configuring integration: {e}")
        
        # Add method response
        try:
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=chatbot_resource_id,
                httpMethod='POST',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
            print("✅ Method response configured")
            
        except Exception as e:
            if "ConflictException" not in str(e):
                print(f"⚠️  Warning configuring method response: {e}")
        
    except Exception as e:
        print(f"❌ Error setting up resources: {e}")
        return
    
    # Step 4: Grant API Gateway permission to invoke Lambda
    try:
        source_arn = f"arn:aws:execute-api:us-east-1:*:{api_id}/*/*"
        
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'apigateway-invoke-{int(time.time())}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        print("✅ Lambda permission granted to API Gateway")
        
    except Exception as e:
        if "ResourceConflictException" not in str(e):
            print(f"⚠️  Warning granting permission: {e}")
    
    # Step 5: Deploy API
    try:
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment'
        )
        print("✅ API deployed to 'prod' stage")
        
        # Construct the endpoint URL
        endpoint_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"🌐 API Gateway URL: {endpoint_url}")
        print(f"🤖 Chatbot endpoint: {endpoint_url}/chatbot")
        
        # Test the endpoint
        print("\n🧪 Testing the endpoint...")
        import requests
        
        test_payload = {
            "message": "Hello! This is a test message.",
            "user_id": "test-user",
            "session_id": "test-session"
        }
        
        try:
            response = requests.post(
                f"{endpoint_url}/chatbot",
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test successful! Response: {result.get('response', 'No response field')}")
            else:
                print(f"⚠️  Test returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"⚠️  Test failed: {e}")
        
        # Update environment file
        env_content = f"""REACT_APP_API_GATEWAY_URL={endpoint_url}
REACT_APP_AWS_REGION=us-east-1
REACT_APP_COGNITO_USER_POOL_ID=us-east-1_TEMP
REACT_APP_COGNITO_CLIENT_ID=TEMP
"""
        
        with open('../frontend/.env', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated frontend/.env with API Gateway URL")
        
    except Exception as e:
        print(f"❌ Error deploying API: {e}")

if __name__ == "__main__":
    main()
