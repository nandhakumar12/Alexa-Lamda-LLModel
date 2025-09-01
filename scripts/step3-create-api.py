#!/usr/bin/env python3
"""
Step 3: Create API Gateway with proper CORS and Lambda integration
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_api_gateway():
    """Create API Gateway with proper CORS and Lambda integration"""
    print("🌐 Creating API Gateway...")
    
    region = 'us-east-1'
    apigateway_client = boto3.client('apigateway', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)
    
    project_name = "nandhakumar-ai-assistant"
    api_name = f"{project_name}-api"
    
    # Load Lambda configuration from previous step
    try:
        with open('step2-config.json', 'r') as f:
            lambda_config = json.load(f)
        lambda_arn = lambda_config['lambda_arn']
        lambda_function_name = lambda_config['lambda_function_name']
        print(f"✅ Loaded Lambda configuration: {lambda_function_name}")
    except Exception as e:
        print(f"❌ Error loading Lambda configuration: {e}")
        print("Please run step2-create-lambda.py first")
        return None
    
    try:
        # Create REST API
        api_response = apigateway_client.create_rest_api(
            name=api_name,
            description='Production API for Nandhakumar AI Assistant',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        
        api_id = api_response['id']
        print(f"✅ API Gateway created: {api_id}")
        
        # Get root resource
        resources = apigateway_client.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create /chat resource
        chat_resource = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='chat'
        )
        chat_resource_id = chat_resource['id']
        print("✅ Created /chat resource")
        
        # Create OPTIONS method for CORS
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Set up OPTIONS integration
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={'application/json': '{"statusCode": 200}'}
        )
        
        # Set up OPTIONS method response
        apigateway_client.put_method_response(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        
        # Set up OPTIONS integration response
        apigateway_client.put_integration_response(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        print("✅ Configured CORS for OPTIONS method")
        
        # Create POST method
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Set up Lambda integration
        lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=chat_resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        print("✅ Configured Lambda integration")
        
        # Add Lambda permission for API Gateway
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{region}:*:{api_id}/*/*"
            )
            print("✅ Added Lambda permission for API Gateway")
        except Exception as e:
            print(f"⚠️ Permission may already exist: {e}")
        
        # Deploy API
        apigateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment'
        )
        
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
        chat_endpoint = f"{api_url}/chat"
        
        print(f"✅ API Gateway deployed: {api_url}")
        print(f"✅ Chat endpoint: {chat_endpoint}")
        
        # Save configuration
        config = {
            'api_id': api_id,
            'api_url': api_url,
            'chat_endpoint': chat_endpoint,
            'region': region
        }
        
        with open('step3-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuration saved to step3-config.json")
        return config
        
    except Exception as e:
        print(f"❌ Error creating API Gateway: {e}")
        return None

if __name__ == "__main__":
    try:
        print("🚀 Step 3: Create API Gateway")
        print("=" * 50)
        
        api_config = create_api_gateway()
        
        if api_config:
            print("\n✅ Step 3 completed successfully!")
            print(f"🔗 API URL: {api_config['api_url']}")
            print(f"💬 Chat Endpoint: {api_config['chat_endpoint']}")
            print("Next: Run step4-create-cognito.py")
        else:
            print("\n❌ Step 3 failed!")
            
    except Exception as e:
        print(f"\n❌ Error in Step 3: {e}")
