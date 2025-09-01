#!/usr/bin/env python3
"""
Quick Deploy Script for Nandhakumar's AI Assistant
This script provides a simplified deployment with better error handling
"""

import boto3
import json
import time
import zipfile
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test AWS credentials and access"""
    print("🔍 Testing AWS credentials...")
    try:
        sts_client = boto3.client('sts', region_name='us-east-1')
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS credentials valid - Account: {identity.get('Account', 'Unknown')}")
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("Please run: aws configure")
        return False
    except Exception as e:
        print(f"❌ AWS access error: {e}")
        return False

def create_lambda_function():
    """Create Lambda function with fallback responses"""
    print("⚡ Creating Lambda function...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = "nandhakumar-ai-assistant-quick"
    role_name = "nandhakumar-ai-assistant-role"
    
    # Create IAM role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        # Clean up existing role
        try:
            iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            iam_client.delete_role(RoleName=role_name)
        except:
            pass
        
        # Create role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        time.sleep(10)  # Wait for propagation
        
    except Exception as e:
        print(f"❌ Error creating IAM role: {e}")
        return None
    
    # Lambda code with intelligent responses
    lambda_code = '''
import json
import requests
import os
from datetime import datetime

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS OK'})}
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        user_message = body.get('message', '').strip()
        user_name = body.get('userName', 'Nandhakumar')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message required'})
            }
        
        # Get intelligent response
        response_text = get_intelligent_response(user_message, user_name)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'user': user_name,
                'model': 'nandhakumar-ai'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_intelligent_response(message, user_name):
    """Generate intelligent responses based on message content"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return f"Hello {user_name}! I'm your personal AI assistant. I'm here to help you with anything you need. How can I assist you today?"
    
    # Music-related responses
    elif any(word in message_lower for word in ['music', 'song', 'artist', 'album', 'spotify', 'playlist', 'listen']):
        return f"Hi {user_name}! I'd love to talk about music with you! I can help you discover new artists, discuss different genres, or chat about your favorite songs. What kind of music are you into? Are you looking for recommendations or want to discuss a particular artist?"
    
    # Technology responses
    elif any(word in message_lower for word in ['technology', 'tech', 'coding', 'programming', 'ai', 'machine learning', 'aws', 'cloud', 'software']):
        return f"Great question about technology, {user_name}! I'm passionate about tech topics. I can help with programming concepts, cloud computing, AI developments, software architecture, and more. What specific technology topic interests you?"
    
    # Personal questions
    elif any(phrase in message_lower for phrase in ['who are you', 'what are you', 'tell me about yourself']):
        return f"I'm {user_name}'s personal AI assistant! I'm designed to be helpful, knowledgeable, and friendly. I can assist with various tasks, answer questions, have engaging conversations about technology, music, and much more. I'm here to make your day easier and more productive!"
    
    # Help requests
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'can you']):
        return f"Of course, {user_name}! I'm here to help. I can assist with answering questions, discussing topics like technology and music, providing information, brainstorming ideas, or just having a friendly conversation. What would you like help with?"
    
    # Weather (mock response)
    elif 'weather' in message_lower:
        return f"I'd love to help with weather information, {user_name}! While I don't have real-time weather data access right now, I recommend checking your local weather app or website for the most accurate forecast. Is there anything else I can help you with?"
    
    # Time-related
    elif any(word in message_lower for word in ['time', 'date', 'today']):
        return f"Hi {user_name}! While I don't have access to real-time data, I can help you with time-related questions or planning. What would you like to know or discuss?"
    
    # General conversation
    else:
        return f"That's interesting, {user_name}! You mentioned: '{message}'. I'd love to learn more about what you're thinking. Could you tell me more about that, or is there something specific I can help you with? I'm here to assist and have engaging conversations!"
'''
    
    try:
        # Create deployment package
        zip_path = '/tmp/lambda_function.zip'
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Delete existing function if it exists
        try:
            lambda_client.delete_function(FunctionName=function_name)
            time.sleep(5)
        except:
            pass
        
        # Create function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Nandhakumar AI Assistant with intelligent responses',
            Timeout=30,
            MemorySize=256
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Lambda function created: {function_arn}")
        return function_arn
        
    except Exception as e:
        print(f"❌ Error creating Lambda function: {e}")
        return None

def create_simple_api(lambda_arn):
    """Create simple API Gateway"""
    print("🌐 Creating API Gateway...")
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Create API
        api = apigateway.create_rest_api(
            name='nandhakumar-ai-api-quick',
            description='Quick API for Nandhakumar AI Assistant'
        )
        api_id = api['id']
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = [r for r in resources['items'] if r['path'] == '/'][0]['id']
        
        # Create chat resource
        chat_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='chat'
        )
        
        # Add POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Add OPTIONS for CORS
        apigateway.put_method(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Configure integrations
        lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        
        # CORS integration
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={'application/json': '{"statusCode": 200}'}
        )
        
        # Method responses
        apigateway.put_method_response(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        
        apigateway.put_integration_response(
            restApiId=api_id,
            resourceId=chat_resource['id'],
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        # Add Lambda permission
        try:
            lambda_client.add_permission(
                FunctionName='nandhakumar-ai-assistant-quick',
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:*:{api_id}/*/*"
            )
        except:
            pass
        
        # Deploy
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chat"
        print(f"✅ API created: {api_url}")
        return api_url
        
    except Exception as e:
        print(f"❌ Error creating API: {e}")
        return None

def main():
    print("🚀 Quick Deploy: Nandhakumar's AI Assistant")
    print("=" * 50)
    
    # Test credentials
    if not test_aws_credentials():
        return False
    
    # Create Lambda
    lambda_arn = create_lambda_function()
    if not lambda_arn:
        return False
    
    # Create API
    api_url = create_simple_api(lambda_arn)
    if not api_url:
        return False
    
    print("\n🎉 QUICK DEPLOYMENT SUCCESSFUL! 🎉")
    print("=" * 50)
    print(f"🔗 API Endpoint: {api_url}")
    print("\n📋 NEXT STEPS:")
    print("1. Test the API endpoint")
    print("2. Create frontend to use this API")
    print("3. Your AI assistant is ready!")
    
    # Save config
    config = {
        'api_url': api_url,
        'lambda_function': 'nandhakumar-ai-assistant-quick',
        'deployment_time': time.time()
    }
    
    with open('quick-deploy-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Deployment failed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
