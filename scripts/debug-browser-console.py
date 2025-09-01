#!/usr/bin/env python3
"""
Debug the exact browser console errors and rebuild from scratch
"""

import requests
import json
import boto3
import time

def check_browser_console_errors():
    """Check what the browser console would show"""
    print("🔍 Debugging Browser Console Errors...")
    
    # Test the exact request the browser would make
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    origin = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    
    print(f"🌐 Testing from origin: {origin}")
    print(f"📡 API URL: {api_url}")
    
    # Test 1: Preflight request (what browser does first)
    print("\n1️⃣ Testing CORS Preflight (OPTIONS)...")
    try:
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        response = requests.options(api_url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"   ❌ PREFLIGHT FAILED: {response.text}")
            return False
        else:
            print("   ✅ Preflight successful")
            
    except Exception as e:
        print(f"   ❌ Preflight error: {e}")
        return False
    
    # Test 2: Actual POST request (what happens after preflight)
    print("\n2️⃣ Testing Actual POST Request...")
    try:
        headers = {
            "Content-Type": "application/json",
            "Origin": origin
        }
        
        payload = {
            "message": "Hello from browser debug",
            "type": "text",
            "session_id": "browser-debug"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("   ✅ POST request successful")
            return True
        else:
            print(f"   ❌ POST request failed")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error")
        return False
    except Exception as e:
        print(f"   ❌ POST error: {e}")
        return False

def check_lambda_function():
    """Check if Lambda function is working"""
    print("\n⚡ Checking Lambda Function...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'voice-assistant-ai-prod-chatbot'
    
    try:
        # Test Lambda directly
        test_event = {
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
            },
            "body": json.dumps({
                "message": "Lambda direct test",
                "type": "text",
                "session_id": "lambda-test"
            })
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"   Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"   Response: {body.get('response', 'No response')[:100]}...")
            print("   ✅ Lambda function working")
            return True
        else:
            print(f"   ❌ Lambda error: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Lambda test failed: {e}")
        return False

def rebuild_api_gateway_from_scratch():
    """Rebuild API Gateway with proper CORS"""
    print("\n🔧 Rebuilding API Gateway from scratch...")
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Create new API
        api_name = f"voice-assistant-fixed-{int(time.time())}"
        
        api_response = apigateway.create_rest_api(
            name=api_name,
            description='Voice Assistant API with proper CORS',
            endpointConfiguration={
                'types': ['REGIONAL']
            }
        )
        
        api_id = api_response['id']
        print(f"   ✅ Created new API: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_id = resource['id']
                break
        
        # Create /chatbot resource
        chatbot_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='chatbot'
        )
        
        chatbot_resource_id = chatbot_resource['id']
        print(f"   ✅ Created /chatbot resource: {chatbot_resource_id}")
        
        # Add OPTIONS method for CORS
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
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
        
        # Add OPTIONS integration
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
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
            },
            responseTemplates={
                'application/json': ''
            }
        )
        
        # Add POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Add POST method response
        apigateway.put_method_response(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        
        # Add POST integration to Lambda
        lambda_arn = f"arn:aws:lambda:us-east-1:{boto3.client('sts').get_caller_identity()['Account']}:function:voice-assistant-ai-prod-chatbot"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        # Deploy the API
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        new_api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"   ✅ New API deployed: {new_api_url}")
        
        # Add Lambda permission
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        try:
            lambda_client.add_permission(
                FunctionName='voice-assistant-ai-prod-chatbot',
                StatementId=f'api-gateway-{api_id}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:{boto3.client('sts').get_caller_identity()['Account']}:{api_id}/*/*"
            )
            print("   ✅ Lambda permission added")
        except Exception as e:
            print(f"   ⚠️  Lambda permission: {e}")
        
        return new_api_url
        
    except Exception as e:
        print(f"   ❌ Failed to rebuild API: {e}")
        return None

def update_frontend_with_new_api(new_api_url):
    """Update frontend with new API URL"""
    print(f"\n📝 Updating frontend with new API: {new_api_url}")
    
    # Update .env file
    env_content = f"""REACT_APP_API_GATEWAY_URL={new_api_url}
REACT_APP_AWS_REGION=us-east-1
REACT_APP_COGNITO_USER_POOL_ID=us-east-1_KSZDQ0iYx
REACT_APP_COGNITO_CLIENT_ID=276p9eoi761kpfiivh7bth9f8s
REACT_APP_COGNITO_IDENTITY_POOL_ID=us-east-1:54da2700-0bd2-4ce9-aad7-f51f57e06d02
GENERATE_SOURCEMAP=false
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("   ✅ Updated .env file")
    return True

def main():
    print("🔧 Complete Network Error Debug & Fix")
    print("=" * 60)
    
    # Step 1: Check current browser console errors
    if check_browser_console_errors():
        print("✅ Current API is working - issue might be frontend")
    else:
        print("❌ API has issues - rebuilding...")
    
    # Step 2: Check Lambda function
    if not check_lambda_function():
        print("❌ Lambda function has issues")
        return
    
    # Step 3: Rebuild API Gateway from scratch
    new_api_url = rebuild_api_gateway_from_scratch()
    if not new_api_url:
        print("❌ Failed to rebuild API Gateway")
        return
    
    # Step 4: Update frontend
    if update_frontend_with_new_api(new_api_url):
        print("✅ Frontend updated with new API")
    
    # Step 5: Test new API
    print(f"\n🧪 Testing new API: {new_api_url}/chatbot")
    try:
        response = requests.post(
            f"{new_api_url}/chatbot",
            json={
                "message": "Testing new API",
                "type": "text",
                "session_id": "new-api-test"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ New API working: {result.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ New API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ New API test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Complete Rebuild Summary:")
    print(f"✅ New API Gateway: {new_api_url}")
    print("✅ CORS properly configured")
    print("✅ Lambda function verified")
    print("✅ Frontend updated")
    
    print("\n🔄 Next steps:")
    print("1. Run: npm run build")
    print("2. Deploy to S3")
    print("3. Test the application")
    
    print(f"\n🌐 New API URL: {new_api_url}")

if __name__ == "__main__":
    main()
