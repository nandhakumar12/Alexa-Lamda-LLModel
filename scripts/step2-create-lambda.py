#!/usr/bin/env python3
"""
Step 2: Create Lambda function with Claude LLM integration
"""

import boto3
import json
import time
import zipfile
import os
from botocore.exceptions import ClientError

def create_lambda_function():
    """Create Lambda function with Claude integration"""
    print("⚡ Creating Lambda function with Claude LLM...")
    
    region = 'us-east-1'
    lambda_client = boto3.client('lambda', region_name=region)
    iam_client = boto3.client('iam', region_name=region)
    
    project_name = "nandhakumar-ai-assistant"
    lambda_function_name = f"{project_name}-claude-llm"
    role_name = f"{project_name}-lambda-role"
    
    # Create IAM role first
    print("🔐 Creating IAM role...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Delete existing role if it exists
        try:
            iam_client.delete_role_policy(RoleName=role_name, PolicyName='LambdaExecutionPolicy')
        except ClientError:
            pass
        try:
            iam_client.detach_role_policy(RoleName=role_name, PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
        except ClientError:
            pass
        try:
            iam_client.delete_role(RoleName=role_name)
        except ClientError:
            pass
            
        # Create new role
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Nandhakumar AI Assistant Lambda function'
        )
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        
        # Wait for role to propagate
        print("⏳ Waiting for IAM role to propagate...")
        time.sleep(15)
        
    except Exception as e:
        print(f"❌ Error creating IAM role: {e}")
        return None
    
    # Lambda function code
    lambda_code = '''
import json
import boto3
import requests
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Production-grade Lambda function for Nandhakumar's AI Assistant
    Integrates with Claude 3 for intelligent responses
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }
    
    try:
        # Parse request body
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = {}
        
        user_message = body.get('message', '').strip()
        user_name = body.get('userName', 'Nandhakumar')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Message is required',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Get Claude API key from environment
        claude_api_key = os.environ.get('CLAUDE_API_KEY')
        if not claude_api_key:
            print("WARNING: CLAUDE_API_KEY not found, using fallback response")
            response_text = get_fallback_response(user_message, user_name)
        else:
            response_text = get_claude_response(user_message, user_name, claude_api_key)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'user': user_name,
                'model': 'claude-3-sonnet' if claude_api_key else 'fallback'
            })
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def get_claude_response(user_message, user_name, api_key):
    """Get response from Claude 3"""
    try:
        # Personalized system prompt for Nandhakumar
        system_prompt = f"""You are {user_name}'s personal AI assistant. You are helpful, friendly, and knowledgeable. 
        Always greet {user_name} warmly and provide thoughtful, personalized responses. 
        You have a warm personality and enjoy discussing technology, music, and helping with various tasks.
        Keep responses conversational and engaging."""
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            print(f"Claude API error: {response.status_code} - {response.text}")
            return get_fallback_response(user_message, user_name)
            
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return get_fallback_response(user_message, user_name)

def get_fallback_response(user_message, user_name):
    """Fallback responses when Claude API is not available"""
    
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    music_keywords = ["music", "song", "artist", "album", "spotify", "playlist"]
    tech_keywords = ["technology", "coding", "programming", "ai", "machine learning", "aws"]
    
    message_lower = user_message.lower()
    
    if any(greeting in message_lower for greeting in greetings):
        return f"Hello {user_name}! I'm your AI assistant. How can I help you today? I'm here to assist with anything you need!"
    
    elif any(keyword in message_lower for keyword in music_keywords):
        return f"Hi {user_name}! I'd love to discuss music with you! I can help you discover new artists, discuss your favorite genres, or chat about the latest music trends. What kind of music are you into?"
    
    elif any(keyword in message_lower for keyword in tech_keywords):
        return f"Great question about technology, {user_name}! I'm passionate about tech topics. I can help discuss programming, cloud computing, AI developments, and more. What specific tech topic interests you?"
    
    elif "who are you" in message_lower or "what are you" in message_lower:
        return f"I'm {user_name}'s personal AI assistant! I'm designed to be helpful, knowledgeable, and friendly. I can assist with various tasks, answer questions, and have engaging conversations. How can I help you today?"
    
    else:
        return f"Hi {user_name}! I understand you said: '{user_message}'. I'm here to help with any questions or tasks you have. What would you like to know or discuss?"
'''
    
    # Create deployment package
    zip_filename = '/tmp/lambda_function.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Read the zip file
    with open(zip_filename, 'rb') as zip_file:
        zip_content = zip_file.read()
    
    # Create Lambda function
    try:
        response = lambda_client.create_function(
            FunctionName=lambda_function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Production-grade AI Assistant for Nandhakumar with Claude LLM integration',
            Timeout=30,
            MemorySize=256,
            Environment={
                'Variables': {
                    'CLAUDE_API_KEY': 'YOUR_CLAUDE_API_KEY_HERE'  # User needs to update this
                }
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Lambda function created: {function_arn}")
        
        # Save configuration
        config = {
            'lambda_function_name': lambda_function_name,
            'lambda_arn': function_arn,
            'role_arn': role_arn
        }
        
        with open('step2-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuration saved to step2-config.json")
        return function_arn
        
    except Exception as e:
        print(f"❌ Error creating Lambda function: {e}")
        return None

if __name__ == "__main__":
    try:
        print("🚀 Step 2: Create Lambda function")
        print("=" * 50)
        
        function_arn = create_lambda_function()
        
        if function_arn:
            print("\n✅ Step 2 completed successfully!")
            print("Next: Run step3-create-api.py")
        else:
            print("\n❌ Step 2 failed!")
            
    except Exception as e:
        print(f"\n❌ Error in Step 2: {e}")
