import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Simple chatbot handler for voice assistant
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        user_id = body.get('user_id', 'anonymous')
        
        # Simple response logic
        if not message:
            response_text = "Hello! I'm your voice assistant. How can I help you today?"
        elif 'hello' in message.lower() or 'hi' in message.lower():
            response_text = f"Hello! Nice to meet you. What would you like to know?"
        elif 'weather' in message.lower():
            response_text = "I'd love to help with weather information! This feature is coming soon."
        elif 'time' in message.lower():
            current_time = datetime.now().strftime("%I:%M %p")
            response_text = f"The current time is {current_time}."
        elif 'help' in message.lower():
            response_text = "I can help you with various tasks! Try asking me about the time, weather, or just say hello!"
        else:
            response_text = f"I heard you say: '{message}'. I'm still learning, but I'm here to help!"
        
        # Log the interaction (optional)
        print(f"User {user_id} said: {message}")
        print(f"Response: {response_text}")
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'message': response_text,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'status': 'success'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Sorry, something went wrong. Please try again.',
                'timestamp': datetime.now().isoformat()
            })
        }
