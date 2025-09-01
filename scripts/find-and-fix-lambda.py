#!/usr/bin/env python3
"""
Find existing Lambda functions and fix the missing Lambda issue
"""

import boto3
import json
import zipfile
import os
from pathlib import Path

def find_and_fix_lambda():
    """Find existing Lambda functions and create/fix the missing one"""
    print("🔍 FINDING & FIXING LAMBDA FUNCTION")
    print("=" * 60)
    
    lambda_client = boto3.client('lambda')
    apigateway_client = boto3.client('apigateway')
    iam_client = boto3.client('iam')
    
    # 1. List all existing Lambda functions
    print("1️⃣ EXISTING LAMBDA FUNCTIONS")
    print("-" * 30)
    
    try:
        functions = lambda_client.list_functions()
        print(f"✅ Found {len(functions['Functions'])} Lambda functions:")
        
        voice_assistant_functions = []
        for func in functions['Functions']:
            print(f"   - {func['FunctionName']} ({func['Runtime']})")
            if 'voice' in func['FunctionName'].lower() or 'assistant' in func['FunctionName'].lower():
                voice_assistant_functions.append(func)
        
        if voice_assistant_functions:
            print(f"\n🎯 Voice Assistant Functions Found: {len(voice_assistant_functions)}")
            for func in voice_assistant_functions:
                print(f"   - {func['FunctionName']}")
                print(f"     Handler: {func['Handler']}")
                print(f"     Runtime: {func['Runtime']}")
                print(f"     Last Modified: {func['LastModified']}")
        else:
            print("\n❌ No voice assistant Lambda functions found!")
            
    except Exception as e:
        print(f"❌ Failed to list functions: {e}")
        return
    
    # 2. Check API Gateway integration
    print("\n2️⃣ API GATEWAY INTEGRATION CHECK")
    print("-" * 30)
    
    api_id = "4po6882mz6"  # Our current API
    
    try:
        # Get the chatbot resource
        resources = apigateway_client.get_resources(restApiId=api_id)
        chatbot_resource = None
        
        for resource in resources['items']:
            if resource['path'] == '/chatbot':
                chatbot_resource = resource
                break
        
        if chatbot_resource:
            print(f"✅ Found /chatbot resource: {chatbot_resource['id']}")
            
            # Check POST method integration
            try:
                method = apigateway_client.get_method(
                    restApiId=api_id,
                    resourceId=chatbot_resource['id'],
                    httpMethod='POST'
                )
                
                integration = method.get('methodIntegration', {})
                if integration:
                    integration_uri = integration.get('uri', '')
                    print(f"   Integration URI: {integration_uri}")
                    
                    # Extract Lambda function name from URI
                    if 'lambda' in integration_uri:
                        # URI format: arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:account:function:function-name/invocations
                        parts = integration_uri.split(':')
                        if len(parts) >= 6:
                            lambda_arn_part = parts[6]  # Should contain function name
                            function_name = lambda_arn_part.split('/')[-2]  # Get function name
                            print(f"   🎯 Integrated Lambda: {function_name}")
                            
                            # Check if this function exists
                            try:
                                lambda_client.get_function(FunctionName=function_name)
                                print(f"   ✅ Lambda function exists!")
                                return function_name  # Function exists, no need to create
                            except:
                                print(f"   ❌ Lambda function '{function_name}' does not exist!")
                                missing_function_name = function_name
                        else:
                            print(f"   ❌ Cannot parse Lambda function name from URI")
                            missing_function_name = "voice-assistant-chatbot"
                    else:
                        print(f"   ❌ Integration is not pointing to Lambda")
                        missing_function_name = "voice-assistant-chatbot"
                else:
                    print(f"   ❌ No integration found")
                    missing_function_name = "voice-assistant-chatbot"
                    
            except Exception as e:
                print(f"   ❌ Failed to get method details: {e}")
                missing_function_name = "voice-assistant-chatbot"
        else:
            print(f"❌ /chatbot resource not found")
            missing_function_name = "voice-assistant-chatbot"
            
    except Exception as e:
        print(f"❌ API Gateway check failed: {e}")
        missing_function_name = "voice-assistant-chatbot"
    
    # 3. Create the missing Lambda function
    print(f"\n3️⃣ CREATING MISSING LAMBDA FUNCTION: {missing_function_name}")
    print("-" * 30)
    
    # Create Lambda function code
    lambda_code = '''
import json
import boto3
import logging
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Voice Assistant Chatbot Lambda Function
    Handles chat requests and returns AI responses
    """
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': ''
            }
        
        # Parse request body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Extract message
        message = body.get('message', 'Hello')
        session_id = body.get('session_id', str(uuid.uuid4()))
        user_id = body.get('user_id', 'anonymous')
        
        logger.info(f"Processing message: {message}")
        
        # Generate response based on message
        response_text = generate_response(message)
        
        # Create response
        response = {
            'response': response_text,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'intent': detect_intent(message),
            'status': 'success'
        }
        
        logger.info(f"Generated response: {response}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        error_response = {
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'error'
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_response)
        }

def generate_response(message):
    """Generate AI response based on message"""
    
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
    
    # Music related
    elif any(word in message_lower for word in ['music', 'song', 'play', 'spotify']):
        return "I can help you with music! I can recommend songs, artists, or help you discover new music. What kind of music are you in the mood for?"
    
    # Weather related
    elif any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy']):
        return "I can help you with weather information! While I don't have real-time weather data right now, I can help you plan based on general weather patterns. What location are you interested in?"
    
    # General assistance
    elif any(word in message_lower for word in ['help', 'assist', 'support']):
        return "I'm here to help! I can assist you with music recommendations, general questions, weather information, and much more. What would you like to know?"
    
    # Thank you
    elif any(word in message_lower for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    # Default response
    else:
        return f"I understand you said: '{message}'. I'm here to help! You can ask me about music, weather, general questions, or just chat with me. What would you like to know?"

def detect_intent(message):
    """Detect the intent of the message"""
    
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return 'greeting'
    elif any(word in message_lower for word in ['music', 'song', 'play']):
        return 'music'
    elif any(word in message_lower for word in ['weather', 'temperature']):
        return 'weather'
    elif any(word in message_lower for word in ['help', 'assist']):
        return 'help'
    elif any(word in message_lower for word in ['thank', 'thanks']):
        return 'gratitude'
    else:
        return 'general'
'''
    
    # Create deployment package
    print("📦 Creating deployment package...")
    
    # Create temporary directory
    temp_dir = Path('temp_lambda')
    temp_dir.mkdir(exist_ok=True)
    
    # Write Lambda code
    lambda_file = temp_dir / 'lambda_function.py'
    with open(lambda_file, 'w') as f:
        f.write(lambda_code)
    
    # Create ZIP file
    zip_path = 'lambda_deployment.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(lambda_file, 'lambda_function.py')
    
    print(f"✅ Created deployment package: {zip_path}")
    
    # Create or get IAM role
    print("👤 Setting up IAM role...")
    
    role_name = 'voice-assistant-lambda-role'
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Try to get existing role
        role = iam_client.get_role(RoleName=role_name)
        role_arn = role['Role']['Arn']
        print(f"✅ Using existing role: {role_arn}")
    except:
        # Create new role
        try:
            role = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for voice assistant Lambda function'
            )
            role_arn = role['Role']['Arn']
            print(f"✅ Created new role: {role_arn}")
            
            # Attach basic Lambda execution policy
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            print("✅ Attached basic execution policy")
            
            # Wait for role to be ready
            import time
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ Failed to create role: {e}")
            return
    
    # Create Lambda function
    print(f"🚀 Creating Lambda function: {missing_function_name}")
    
    try:
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.create_function(
            FunctionName=missing_function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Voice Assistant Chatbot Function',
            Timeout=30,
            MemorySize=256,
            Environment={
                'Variables': {
                    'ENVIRONMENT': 'production'
                }
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_arn}")
        
        # Add API Gateway permission
        print("🔗 Adding API Gateway permission...")
        
        try:
            lambda_client.add_permission(
                FunctionName=missing_function_name,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:us-east-1:*:{api_id}/*/*'
            )
            print("✅ Added API Gateway permission")
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                print("✅ API Gateway permission already exists")
            else:
                print(f"⚠️  Permission warning: {e}")
        
        # Update API Gateway integration
        print("🔗 Updating API Gateway integration...")
        
        integration_uri = f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations'
        
        try:
            apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=chatbot_resource['id'],
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=integration_uri
            )
            print("✅ Updated API Gateway integration")
            
            # Deploy API
            apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod',
                description=f'Updated with Lambda function {missing_function_name}'
            )
            print("✅ Deployed API Gateway")
            
        except Exception as e:
            print(f"❌ Failed to update API Gateway: {e}")
        
        # Clean up
        os.remove(zip_path)
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n🎉 SUCCESS! Lambda function '{missing_function_name}' created and integrated!")
        return missing_function_name
        
    except Exception as e:
        print(f"❌ Failed to create Lambda function: {e}")
        return None

if __name__ == "__main__":
    result = find_and_fix_lambda()
    if result:
        print(f"\n✅ Lambda function ready: {result}")
        print(f"🌐 API URL: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot")
    else:
        print(f"\n❌ Failed to create Lambda function")
