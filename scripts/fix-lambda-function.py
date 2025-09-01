#!/usr/bin/env python3
"""
Fix the Lambda function to work properly with API Gateway
"""

import boto3
import json
import zipfile
import io

lambda_client = boto3.client('lambda', region_name='us-east-1')

def create_lambda_code():
    """Create a working Lambda function code"""
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
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({
                    'error': 'Message is required',
                    'session_id': session_id
                })
            }
        
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'session_id': body.get('session_id', str(uuid.uuid4())) if 'body' in locals() else str(uuid.uuid4())
            })
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
    return lambda_code

def main():
    print("🔧 Fixing Lambda function...")
    
    function_name = 'voice-assistant-ai-prod-chatbot'
    
    try:
        # Create the Lambda code
        lambda_code = create_lambda_code()
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_content = zip_buffer.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Updated Lambda function: {function_name}")
        print(f"   Version: {response['Version']}")
        print(f"   Last Modified: {response['LastModified']}")
        
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
        else:
            print(f"❌ Test failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    main()
