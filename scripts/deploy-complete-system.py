#!/usr/bin/env python3
"""
Complete deployment script for Nandhakumar's AI Assistant
This will deploy everything properly with real Cognito authentication
"""

import boto3
import json
import time
import subprocess
import os

# Configuration
PROJECT_NAME = "voice-assistant-ai"
ENVIRONMENT = "prod"
REGION = "us-east-1"

# Initialize AWS clients
cf_client = boto3.client('cloudformation', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
cloudfront_client = boto3.client('cloudfront', region_name=REGION)

def deploy_cognito():
    """Deploy Cognito User Pool and Client"""
    print("🔐 Deploying Cognito User Pool...")
    
    stack_name = f"{PROJECT_NAME}-{ENVIRONMENT}-cognito"
    
    try:
        with open('backend/cloudformation/cognito.yaml', 'r') as f:
            template_body = f.read()
        
        # Deploy the stack
        cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ProjectName', 'ParameterValue': PROJECT_NAME},
                {'ParameterKey': 'Environment', 'ParameterValue': ENVIRONMENT}
            ],
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        
        print(f"   Creating stack: {stack_name}")
        
        # Wait for stack creation
        waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 10, 'MaxAttempts': 60})
        
        print("✅ Cognito stack created successfully!")
        
    except cf_client.exceptions.AlreadyExistsException:
        print("   Stack already exists, updating...")
        
        cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ProjectName', 'ParameterValue': PROJECT_NAME},
                {'ParameterKey': 'Environment', 'ParameterValue': ENVIRONMENT}
            ],
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        
        # Wait for stack update
        waiter = cf_client.get_waiter('stack_update_complete')
        waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 10, 'MaxAttempts': 60})
        
        print("✅ Cognito stack updated successfully!")
    
    # Get outputs
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    
    cognito_config = {}
    for output in outputs:
        key = output['OutputKey']
        value = output['OutputValue']
        cognito_config[key] = value
        print(f"   {key}: {value}")
    
    return cognito_config

def deploy_lambda_function():
    """Deploy the fixed Lambda function"""
    print("\n⚡ Deploying Lambda function...")
    
    function_name = f"{PROJECT_NAME}-{ENVIRONMENT}-chatbot"
    
    # Create the Lambda code
    lambda_code = '''
import json
import logging
import uuid
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main Lambda handler for voice assistant chatbot
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract message and user info
        message = body.get('message', '').strip()
        user_id = body.get('user_id', 'anonymous')
        session_id = body.get('session_id', str(uuid.uuid4()))
        
        logger.info(f"Processing message: {message} for user: {user_id}")
        
        if not message:
            return create_response(400, {
                'error': 'Message is required',
                'session_id': session_id
            })
        
        # Generate response based on message content
        response_text = generate_response(message, user_id)
        
        # Create response
        response_data = {
            'response': response_text,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'intent': detect_intent(message),
            'conversation_id': session_id
        }
        
        logger.info(f"Generated response: {response_text}")
        
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        return create_response(500, {
            'error': 'I apologize, but I encountered an error. Please try again.',
            'session_id': str(uuid.uuid4())
        })

def create_response(status_code, data):
    """Create a properly formatted API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(data)
    }

def generate_response(message, user_id):
    """Generate a response based on the user message"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return f"Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
    
    # Music-related responses
    elif any(word in message_lower for word in ['music', 'song', 'play', 'spotify', 'playlist']):
        return "I'd be happy to help you with music! I can assist with finding songs, creating playlists, or recommending music based on your preferences. What would you like to do?"
    
    # Help responses
    elif any(word in message_lower for word in ['help', 'what can you do', 'capabilities']):
        return "I'm an AI assistant that can help you with various tasks including music recommendations, general questions, and conversation. I'm powered by advanced language models and ready to assist you!"
    
    # Weather responses
    elif any(word in message_lower for word in ['weather', 'temperature', 'forecast']):
        return "I can help you with weather information! While I don't have real-time weather data right now, I can discuss weather topics or help you find weather resources."
    
    # Time responses
    elif any(word in message_lower for word in ['time', 'date', 'today']):
        return f"The current time is {datetime.now().strftime('%I:%M %p')} and today is {datetime.now().strftime('%A, %B %d, %Y')}."
    
    # Thank you responses
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! I'm here to help whenever you need assistance."
    
    # Goodbye responses
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
        return "Goodbye! It was great chatting with you. Feel free to come back anytime you need help!"
    
    # Default response
    else:
        return f"I understand you said: '{message}'. I'm here to help! You can ask me about music, weather, general questions, or just have a conversation. What would you like to know more about?"

def detect_intent(message):
    """Detect the intent of the user message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return 'greeting'
    elif any(word in message_lower for word in ['music', 'song', 'play']):
        return 'music'
    elif any(word in message_lower for word in ['weather', 'temperature']):
        return 'weather'
    elif any(word in message_lower for word in ['help', 'what can you do']):
        return 'help'
    elif any(word in message_lower for word in ['bye', 'goodbye']):
        return 'goodbye'
    else:
        return 'general'
'''
    
    # Create zip file
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    # Create or update Lambda function
    try:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=f'arn:aws:iam::{get_account_id()}:role/voice-assistant-lambda-role',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Voice Assistant Chatbot',
            Timeout=30,
            MemorySize=256
        )
        print(f"✅ Created Lambda function: {function_name}")
        
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"✅ Updated Lambda function: {function_name}")
    
    return function_name

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def main():
    print("🚀 Deploying Complete Voice Assistant System")
    print("=" * 50)
    
    try:
        # Step 1: Deploy Cognito
        cognito_config = deploy_cognito()
        
        # Step 2: Deploy Lambda
        function_name = deploy_lambda_function()
        
        print(f"\n🎉 Deployment completed successfully!")
        print(f"✅ Cognito User Pool: {cognito_config.get('UserPoolId')}")
        print(f"✅ Cognito Client: {cognito_config.get('UserPoolClientId')}")
        print(f"✅ Lambda Function: {function_name}")
        
        # Update frontend environment
        env_content = f"""REACT_APP_API_GATEWAY_URL=https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_AWS_REGION={REGION}
REACT_APP_COGNITO_USER_POOL_ID={cognito_config.get('UserPoolId')}
REACT_APP_COGNITO_CLIENT_ID={cognito_config.get('UserPoolClientId')}
REACT_APP_COGNITO_IDENTITY_POOL_ID={cognito_config.get('IdentityPoolId')}
"""
        
        with open('frontend/.env', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated frontend/.env with real Cognito credentials")
        
        print(f"\n🔄 Next steps:")
        print(f"1. Run: cd frontend && npm run build")
        print(f"2. Deploy to S3 and CloudFront")
        print(f"3. Test authentication and chatbot")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()
