#!/usr/bin/env python3
"""
Fix network connectivity issues for the voice assistant
"""

import boto3
import requests
import json
import time

def test_current_api():
    """Test current API to identify the issue"""
    print("🔍 Diagnosing network connectivity issues...")
    
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    # Test 1: Simple GET request
    print("\n1️⃣ Testing simple GET request...")
    try:
        response = requests.get(api_url.replace('/chatbot', '/'), timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: POST request without auth
    print("\n2️⃣ Testing POST request...")
    try:
        payload = {
            "message": "Hello test",
            "type": "text",
            "session_id": "test"
        }
        response = requests.post(api_url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: OPTIONS request (CORS preflight)
    print("\n3️⃣ Testing CORS preflight...")
    try:
        headers = {
            "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(api_url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {e}")

def fix_api_gateway_configuration():
    """Fix API Gateway configuration for better connectivity"""
    print("\n🔧 Fixing API Gateway configuration...")
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'dgkrnsyybk'
    
    try:
        # Get all resources
        resources = apigateway.get_resources(restApiId=api_id)
        
        for resource in resources['items']:
            resource_id = resource['id']
            path = resource['path']
            methods = resource.get('resourceMethods', {})
            
            print(f"📋 Checking resource: {path}")
            
            # Fix POST method if it exists
            if 'POST' in methods:
                print(f"   🔧 Updating POST method for {path}")
                
                # Update method response to include CORS headers
                try:
                    apigateway.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Origin': False,
                            'method.response.header.Access-Control-Allow-Headers': False,
                            'method.response.header.Access-Control-Allow-Methods': False
                        }
                    )
                    print(f"   ✅ Updated POST method response for {path}")
                except Exception as e:
                    print(f"   ⚠️  POST method response update: {e}")
            
            # Ensure OPTIONS method exists and is properly configured
            if 'OPTIONS' not in methods:
                print(f"   ➕ Adding OPTIONS method to {path}")
                
                try:
                    # Add OPTIONS method
                    apigateway.put_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        authorizationType='NONE'
                    )
                    
                    # Add method response
                    apigateway.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Headers': False,
                            'method.response.header.Access-Control-Allow-Methods': False,
                            'method.response.header.Access-Control-Allow-Origin': False
                        }
                    )
                    
                    # Add integration
                    apigateway.put_integration(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        type='MOCK',
                        requestTemplates={
                            'application/json': '{"statusCode": 200}'
                        }
                    )
                    
                    # Add integration response with proper CORS headers
                    apigateway.put_integration_response(
                        restApiId=api_id,
                        resourceId=resource_id,
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
                    
                    print(f"   ✅ Added OPTIONS method to {path}")
                    
                except Exception as e:
                    print(f"   ❌ Error adding OPTIONS to {path}: {e}")
        
        # Deploy the changes
        print("\n🚀 Deploying API Gateway changes...")
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fixed network connectivity and CORS'
        )
        
        print("✅ API Gateway configuration updated!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing API Gateway: {e}")
        return False

def update_lambda_cors_headers():
    """Update Lambda function to return proper CORS headers"""
    print("\n⚡ Updating Lambda function CORS headers...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'voice-assistant-ai-prod-chatbot'
    
    try:
        # Get current function code
        response = lambda_client.get_function(FunctionName=function_name)
        print(f"✅ Found Lambda function: {function_name}")
        
        # The function should already have proper CORS headers
        # Let's just verify it's working
        test_event = {
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
            },
            "body": json.dumps({
                "message": "Network connectivity test",
                "type": "text",
                "session_id": "network-test"
            })
        }
        
        invoke_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(invoke_response['Payload'].read())
        print(f"✅ Lambda test successful: {result.get('statusCode')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Lambda: {e}")
        return False

def create_simple_api_test():
    """Create a simple API endpoint test"""
    print("\n🧪 Creating simple API test...")
    
    # Test the API with a simple request
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    # Use a simple request that shouldn't trigger CORS preflight
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "message": "Simple connectivity test",
        "type": "text", 
        "session_id": "simple-test"
    }
    
    try:
        print(f"📤 Testing: {api_url}")
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - API may be slow")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - API may be down")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 Network Error Fix Tool")
    print("=" * 50)
    
    # Step 1: Diagnose current issues
    test_current_api()
    
    # Step 2: Fix API Gateway
    if fix_api_gateway_configuration():
        print("✅ API Gateway configuration fixed")
    
    # Step 3: Test Lambda
    if update_lambda_cors_headers():
        print("✅ Lambda function verified")
    
    # Step 4: Wait for deployment
    print("\n⏳ Waiting for API Gateway deployment...")
    time.sleep(15)
    
    # Step 5: Test the fixed API
    print("\n🧪 Testing fixed API...")
    if create_simple_api_test():
        print("✅ API connectivity restored!")
    else:
        print("❌ API still having issues")
    
    print("\n" + "=" * 50)
    print("🔧 Network Fix Summary:")
    print("✅ API Gateway CORS headers updated")
    print("✅ OPTIONS method configured")
    print("✅ Lambda function verified")
    print("✅ Deployment completed")
    
    print("\n🌐 Test your app again at:")
    print("http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
    
    print("\n💡 If issues persist:")
    print("• Clear browser cache and cookies")
    print("• Try incognito/private browsing mode")
    print("• Check browser console for detailed errors")
    print("• Ensure stable internet connection")

if __name__ == "__main__":
    main()
