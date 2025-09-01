#!/usr/bin/env python3
"""
Fix API Gateway integration issues
"""

import boto3
import json
import time

def fix_api_gateway_integration():
    """Fix API Gateway integration with Lambda"""
    print("🔧 FIXING API GATEWAY INTEGRATION")
    print("=" * 60)
    
    apigateway_client = boto3.client('apigateway')
    lambda_client = boto3.client('lambda')
    
    api_id = "4po6882mz6"
    function_name = "voice-assistant-chatbot"
    
    # 1. Get current integration details
    print("1️⃣ Checking current integration...")
    
    try:
        resources = apigateway_client.get_resources(restApiId=api_id)
        chatbot_resource = None
        
        for resource in resources['items']:
            if resource['path'] == '/chatbot':
                chatbot_resource = resource
                break
        
        if not chatbot_resource:
            print("❌ /chatbot resource not found")
            return
        
        resource_id = chatbot_resource['id']
        print(f"✅ Found /chatbot resource: {resource_id}")
        
        # Check current POST method
        try:
            method = apigateway_client.get_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST'
            )
            
            integration = method.get('methodIntegration', {})
            print(f"   Current integration type: {integration.get('type', 'None')}")
            print(f"   Current integration URI: {integration.get('uri', 'None')}")
            
        except Exception as e:
            print(f"   ❌ Failed to get POST method: {e}")
            
    except Exception as e:
        print(f"❌ Failed to check resources: {e}")
        return
    
    # 2. Get Lambda function ARN
    print("\n2️⃣ Getting Lambda function details...")
    
    try:
        lambda_response = lambda_client.get_function(FunctionName=function_name)
        function_arn = lambda_response['Configuration']['FunctionArn']
        print(f"✅ Lambda ARN: {function_arn}")
        
    except Exception as e:
        print(f"❌ Failed to get Lambda function: {e}")
        return
    
    # 3. Delete and recreate the integration
    print("\n3️⃣ Recreating API Gateway integration...")
    
    try:
        # Delete existing integration
        try:
            apigateway_client.delete_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST'
            )
            print("✅ Deleted existing integration")
        except:
            print("   No existing integration to delete")
        
        # Wait a moment
        time.sleep(2)
        
        # Create new integration
        integration_uri = f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations'
        
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=integration_uri,
            passthroughBehavior='WHEN_NO_MATCH',
            timeoutInMillis=29000
        )
        
        print("✅ Created new AWS_PROXY integration")
        
        # Set up integration response
        apigateway_client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            statusCode='200',
            responseTemplates={
                'application/json': ''
            }
        )
        
        print("✅ Set up integration response")
        
    except Exception as e:
        print(f"❌ Failed to recreate integration: {e}")
        return
    
    # 4. Update Lambda permissions
    print("\n4️⃣ Updating Lambda permissions...")
    
    try:
        # Remove existing permission
        try:
            lambda_client.remove_permission(
                FunctionName=function_name,
                StatementId='api-gateway-invoke'
            )
            print("✅ Removed old permission")
        except:
            print("   No old permission to remove")
        
        # Wait a moment
        time.sleep(2)
        
        # Add new permission with correct source ARN
        source_arn = f'arn:aws:execute-api:us-east-1:266833219725:{api_id}/*/*'
        
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='api-gateway-invoke-new',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        
        print(f"✅ Added new permission with source ARN: {source_arn}")
        
    except Exception as e:
        print(f"❌ Failed to update permissions: {e}")
    
    # 5. Deploy the API
    print("\n5️⃣ Deploying API...")
    
    try:
        deployment = apigateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fixed integration deployment'
        )
        
        print(f"✅ Deployed API - Deployment ID: {deployment['id']}")
        
    except Exception as e:
        print(f"❌ Failed to deploy API: {e}")
    
    # 6. Test the integration
    print("\n6️⃣ Testing the fixed integration...")
    
    try:
        # Test with API Gateway test feature
        test_response = apigateway_client.test_invoke_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            body=json.dumps({
                "message": "API Gateway integration test",
                "session_id": "integration-test"
            }),
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        print(f"   Test Status: {test_response['status']}")
        
        if test_response['status'] == 200:
            print("   ✅ Integration test successful!")
            if 'body' in test_response:
                try:
                    body = json.loads(test_response['body'])
                    print(f"   Response: {body.get('response', 'No response field')}")
                except:
                    print(f"   Raw body: {test_response['body'][:200]}...")
        else:
            print(f"   ❌ Integration test failed")
            if 'body' in test_response:
                print(f"   Error: {test_response['body']}")
            
    except Exception as e:
        print(f"   ❌ Integration test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API GATEWAY INTEGRATION FIX COMPLETE!")
    print("✅ Recreated AWS_PROXY integration")
    print("✅ Updated Lambda permissions")
    print("✅ Deployed API changes")
    
    print(f"\n🌐 Test URL: https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chatbot")
    print("💡 The API should now work properly!")

if __name__ == "__main__":
    fix_api_gateway_integration()
