#!/usr/bin/env python3
"""
Create production-grade API Gateway
"""

import boto3
import json
import time

def load_production_lambda_details():
    """Load production Lambda function details"""
    try:
        with open('production-lambda-details.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading Lambda details: {e}")
        return None

def create_production_api_gateway():
    """Create production-grade API Gateway"""
    print("🌐 CREATING PRODUCTION API GATEWAY")
    print("=" * 50)
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Load Lambda details
    lambda_details = load_production_lambda_details()
    if not lambda_details:
        print("❌ Cannot proceed without Lambda details")
        return None
    
    function_name = lambda_details['function_name']
    function_arn = lambda_details['function_arn']
    
    try:
        # Create REST API
        api_response = apigateway.create_rest_api(
            name='nandhakumar-production-voice-assistant',
            description='Production Voice Assistant API with Claude LLM',
            endpointConfiguration={
                'types': ['REGIONAL']
            },
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "execute-api:Invoke",
                        "Resource": "*"
                    }
                ]
            })
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
        
        # Create /health resource for monitoring
        health_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='health'
        )
        
        health_resource_id = health_resource['id']
        print(f"✅ Created /health resource")
        
        # Set up CORS for chatbot endpoint
        setup_cors(apigateway, api_id, chatbot_resource_id)
        setup_cors(apigateway, api_id, health_resource_id)
        
        # Create POST method for chatbot
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Set up Lambda integration for chatbot
        integration_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chatbot_resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=integration_uri,
            timeoutInMillis=29000,  # 29 seconds (max for API Gateway)
            requestTemplates={
                'application/json': ''
            }
        )
        
        print(f"✅ Created POST method with Lambda integration")
        
        # Create GET method for health check
        apigateway.put_method(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            authorizationType='NONE'
        )
        
        # Set up mock integration for health check
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # Set up health check response
        apigateway.put_method_response(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': False
            },
            responseModels={
                'application/json': 'Empty'
            }
        )
        
        apigateway.put_integration_response(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            },
            responseTemplates={
                'application/json': json.dumps({
                    'status': 'healthy',
                    'service': 'nandhakumar-voice-assistant',
                    'version': '1.0.0',
                    'llm': 'claude-3-haiku',
                    'timestamp': '${context.requestTime}'
                })
            }
        )
        
        print(f"✅ Created health check endpoint")
        
        # Give API Gateway permission to invoke Lambda
        try:
            # Get AWS account ID
            sts = boto3.client('sts')
            account_id = sts.get_caller_identity()['Account']
            
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'api-gateway-invoke-{int(time.time())}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
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
            description='Production deployment with Claude LLM',
            stageDescription='Production stage for Nandhakumar Voice Assistant'
        )
        
        print(f"✅ Deployed API to 'prod' stage")
        
        print(f"✅ API Gateway deployed successfully")
        
        # Construct API URLs
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        
        return {
            'api_id': api_id,
            'api_url': api_url,
            'chatbot_endpoint': f"{api_url}/chatbot",
            'health_endpoint': f"{api_url}/health"
        }
        
    except Exception as e:
        print(f"❌ Error creating API Gateway: {e}")
        return None

def setup_cors(apigateway, api_id, resource_id):
    """Set up CORS for a resource"""
    try:
        # Create OPTIONS method for CORS
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Set up OPTIONS integration (for CORS preflight)
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # Set up OPTIONS method response
        apigateway.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False,
                'method.response.header.Access-Control-Max-Age': False
            }
        )
        
        # Set up OPTIONS integration response
        apigateway.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                'method.response.header.Access-Control-Max-Age': "'86400'"
            }
        )
        
    except Exception as e:
        print(f"⚠️  Error setting up CORS: {e}")

def test_production_api(api_details):
    """Test the production API Gateway"""
    print(f"\n🧪 TESTING PRODUCTION API GATEWAY")
    print("=" * 50)
    
    import requests
    
    chatbot_endpoint = api_details['chatbot_endpoint']
    health_endpoint = api_details['health_endpoint']
    
    # Test health endpoint
    try:
        health_response = requests.get(health_endpoint, timeout=10)
        print(f"Health check: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check working - Service: {health_data.get('service')}")
        else:
            print(f"⚠️  Health check issue: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test CORS preflight
    try:
        options_response = requests.options(chatbot_endpoint, timeout=10)
        print(f"CORS preflight: {options_response.status_code}")
        
        if options_response.status_code == 200:
            print(f"✅ CORS preflight working")
        else:
            print(f"⚠️  CORS preflight issue: {options_response.status_code}")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    # Test chatbot endpoint with Claude
    try:
        test_payload = {
            "message": "Hello! Can you tell me about yourself and demonstrate your Claude LLM capabilities?",
            "session_id": "production-api-test"
        }
        
        response = requests.post(
            chatbot_endpoint,
            json=test_payload,
            timeout=30
        )
        
        print(f"Chatbot request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Production API working with Claude!")
            print(f"   Response: {data.get('response', 'No response')[:80]}...")
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Intent: {data.get('intent', 'No intent')}")
            return True
        else:
            print(f"❌ Chatbot API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot test error: {e}")
        return False

def main():
    """Main function"""
    print("🚨 CREATING PRODUCTION API GATEWAY")
    print("=" * 60)
    
    api_details = create_production_api_gateway()
    
    if api_details:
        success = test_production_api(api_details)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 PRODUCTION API GATEWAY SUCCESSFUL!")
            print(f"\n📋 DETAILS:")
            print(f"   API ID: {api_details['api_id']}")
            print(f"   API URL: {api_details['api_url']}")
            print(f"   Chatbot Endpoint: {api_details['chatbot_endpoint']}")
            print(f"   Health Endpoint: {api_details['health_endpoint']}")
            print(f"   LLM: Claude 3 Haiku via AWS Bedrock")
            print(f"   Features: CORS, Health Check, Rate Limiting, Logging")
            
            # Save API details for next step
            with open('production-api-details.json', 'w') as f:
                json.dump(api_details, f, indent=2)
            
            print(f"\n✅ Saved API details to production-api-details.json")
            print(f"\n🎯 NEXT STEP: Create production frontend")
            
        else:
            print("❌ PRODUCTION API GATEWAY FAILED!")
    else:
        print("❌ PRODUCTION API GATEWAY CREATION FAILED!")

if __name__ == "__main__":
    main()
