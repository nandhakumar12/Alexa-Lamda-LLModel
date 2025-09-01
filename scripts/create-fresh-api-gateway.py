#!/usr/bin/env python3
"""
Create a fresh API Gateway for the chatbot
"""

import boto3
import json
import time

def load_lambda_details():
    """Load Lambda function details"""
    try:
        with open('lambda-details.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading Lambda details: {e}")
        return None

def create_api_gateway():
    """Create a fresh API Gateway"""
    print("🌐 CREATING FRESH API GATEWAY")
    print("=" * 50)
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Load Lambda details
    lambda_details = load_lambda_details()
    if not lambda_details:
        print("❌ Cannot proceed without Lambda details")
        return None
    
    function_name = lambda_details['function_name']
    function_arn = lambda_details['function_arn']
    
    try:
        # Create REST API
        api_response = apigateway.create_rest_api(
            name='nandhakumar-fresh-voice-assistant',
            description='Fresh Voice Assistant API without authentication',
            endpointConfiguration={
                'types': ['REGIONAL']
            }
        )
        
        api_id = api_response['id']
        print(f"✅ Created API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_resource_id = None
        
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create /chatbot resource
        chatbot_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='chatbot'
        )
        
        chatbot_resource_id = chatbot_resource['id']
        print(f"✅ Created /chatbot resource")
        
        # Create OPTIONS method for CORS
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Set up OPTIONS integration (for CORS preflight)
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # Set up OPTIONS method response
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
        
        # Set up OPTIONS integration response
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
        
        print(f"✅ Created OPTIONS method for CORS")
        
        # Create POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Set up Lambda integration
        integration_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=integration_uri
        )
        
        print(f"✅ Created POST method with Lambda integration")
        
        # Give API Gateway permission to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'api-gateway-invoke-{int(time.time())}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:*:{api_id}/*/*"
            )
            print(f"✅ Added Lambda invoke permission")
        except Exception as e:
            if "ResourceConflictException" in str(e):
                print(f"✅ Lambda permission already exists")
            else:
                print(f"⚠️  Error adding Lambda permission: {e}")
        
        # Deploy the API
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment of fresh voice assistant'
        )
        
        print(f"✅ Deployed API to 'prod' stage")
        
        # Construct API URL
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        
        return {
            'api_id': api_id,
            'api_url': api_url,
            'chatbot_endpoint': f"{api_url}/chatbot"
        }
        
    except Exception as e:
        print(f"❌ Error creating API Gateway: {e}")
        return None

def test_api_gateway(api_details):
    """Test the API Gateway"""
    print(f"\n🧪 TESTING API GATEWAY")
    print("=" * 50)
    
    import requests
    
    chatbot_endpoint = api_details['chatbot_endpoint']
    
    # Test OPTIONS (CORS preflight)
    try:
        options_response = requests.options(chatbot_endpoint, timeout=10)
        print(f"OPTIONS request: {options_response.status_code}")
        
        if options_response.status_code == 200:
            print(f"✅ CORS preflight working")
        else:
            print(f"⚠️  CORS preflight issue: {options_response.status_code}")
            
    except Exception as e:
        print(f"❌ OPTIONS test error: {e}")
    
    # Test POST
    try:
        test_payload = {
            "message": "Hello! This is a test from the API Gateway setup.",
            "session_id": "api-test-session"
        }
        
        response = requests.post(
            chatbot_endpoint,
            json=test_payload,
            timeout=15
        )
        
        print(f"POST request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Gateway working!")
            print(f"   Response: {data.get('response', 'No response')[:50]}...")
            print(f"   Intent: {data.get('intent', 'No intent')}")
            return True
        else:
            print(f"❌ API Gateway failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ POST test error: {e}")
        return False

def main():
    """Main function"""
    print("🚨 CREATING FRESH API GATEWAY")
    print("=" * 60)
    
    api_details = create_api_gateway()
    
    if api_details:
        success = test_api_gateway(api_details)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 API GATEWAY CREATION SUCCESSFUL!")
            print(f"\n📋 DETAILS:")
            print(f"   API ID: {api_details['api_id']}")
            print(f"   API URL: {api_details['api_url']}")
            print(f"   Chatbot Endpoint: {api_details['chatbot_endpoint']}")
            
            print(f"\n🎯 NEXT STEP: Update frontend and deploy")
            
            # Save API details for next step
            with open('api-details.json', 'w') as f:
                json.dump(api_details, f, indent=2)
            
            print(f"✅ Saved API details to api-details.json")
            
        else:
            print("❌ API GATEWAY CREATION FAILED!")
    else:
        print("❌ API GATEWAY CREATION FAILED!")

if __name__ == "__main__":
    main()
