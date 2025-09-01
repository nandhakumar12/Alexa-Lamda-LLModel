#!/usr/bin/env python3
"""
Recreate Lambda function with working code
"""

import boto3
import json
import zipfile
import io
import time

lambda_client = boto3.client('lambda', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def create_lambda_code():
    """Create working Lambda function code"""
    return '''
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
            'error': 'Internal server error',
            'message': str(e),
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

def main():
    print("🔧 Recreating Lambda function...")
    
    account_id = get_account_id()
    function_name = 'voice-assistant-chatbot-fixed'
    
    # Create IAM role for Lambda
    role_name = 'voice-assistant-lambda-role'
    
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
        # Try to create the role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for voice assistant Lambda function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Wait for role to be ready
        time.sleep(10)
        
    except Exception as e:
        if "EntityAlreadyExists" in str(e):
            role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
            print(f"✅ Using existing IAM role: {role_arn}")
        else:
            print(f"❌ Error creating IAM role: {e}")
            return
    
    try:
        # Delete existing function if it exists
        try:
            lambda_client.delete_function(FunctionName=function_name)
            print(f"🗑️  Deleted existing function: {function_name}")
            time.sleep(5)
        except:
            pass
        
        # Create the Lambda code
        lambda_code = create_lambda_code()
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_content = zip_buffer.read()
        
        # Create the Lambda function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Fixed voice assistant chatbot',
            Timeout=30,
            MemorySize=256
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_name}")
        print(f"   ARN: {function_arn}")
        
        # Test the function
        print("\n🧪 Testing Lambda function...")
        
        test_event = {
            'body': json.dumps({
                'message': 'Hello! Can you help me?',
                'user_id': 'test-user'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        test_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(test_response['Payload'].read())
        print(f"📊 Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"✅ Test successful! Response: {body.get('response')}")
            
            # Now update the API Gateway to use this function
            print("\n🔗 Updating API Gateway...")
            
            # Import the API Gateway fix script
            import sys
            sys.path.append('.')
            
            # Update API Gateway to use new function
            apigateway = boto3.client('apigateway', region_name='us-east-1')
            
            # Find the API Gateway
            apis = apigateway.get_rest_apis()
            target_api = None
            
            for api in apis['items']:
                if api['name'] == 'voice-assistant-clean-api':
                    target_api = api
                    break
            
            if target_api:
                api_id = target_api['id']
                
                # Get resources
                resources = apigateway.get_resources(restApiId=api_id)
                chatbot_resource_id = None
                
                for resource in resources['items']:
                    if resource['path'] == '/chatbot':
                        chatbot_resource_id = resource['id']
                        break
                
                if chatbot_resource_id:
                    # Update the integration to use new function
                    lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
                    
                    apigateway.put_integration(
                        restApiId=api_id,
                        resourceId=chatbot_resource_id,
                        httpMethod='POST',
                        type='AWS_PROXY',
                        integrationHttpMethod='POST',
                        uri=lambda_uri
                    )
                    
                    # Grant permission
                    source_arn = f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
                    
                    try:
                        lambda_client.add_permission(
                            FunctionName=function_name,
                            StatementId=f'apigateway-{api_id}-{int(time.time())}',
                            Action='lambda:InvokeFunction',
                            Principal='apigateway.amazonaws.com',
                            SourceArn=source_arn
                        )
                    except:
                        pass
                    
                    # Redeploy
                    apigateway.create_deployment(
                        restApiId=api_id,
                        stageName='prod'
                    )
                    
                    endpoint_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
                    print(f"✅ Updated API Gateway: {endpoint_url}/chatbot")
                    
                    # Test the API
                    print("\n🌐 Testing API Gateway...")
                    import requests
                    
                    test_data = {
                        "message": "Hello! Can you help me?",
                        "user_id": "test-user"
                    }
                    
                    try:
                        response = requests.post(f"{endpoint_url}/chatbot", json=test_data, timeout=15)
                        print(f"📊 API Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"✅ API Test successful! Response: {result.get('response')}")
                        else:
                            print(f"❌ API Error: {response.text}")
                            
                    except Exception as e:
                        print(f"❌ API Test failed: {e}")
            
        else:
            print(f"❌ Test failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Lambda function: {e}")
        return False

if __name__ == "__main__":
    main()
