import json
import random
import time

def lambda_handler(event, context):
    """Simple chatbot Lambda function without authentication"""
    
    print(f"Received event: {json.dumps(event)}")
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            body = event
        
        message = body.get('message', '').strip()
        session_id = body.get('session_id', f'session-{int(time.time())}')
        
        # Simple AI responses
        responses = {
            'greeting': [
                "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?",
                "Hi there! Welcome to Nandhakumar's AI Assistant. What can I do for you?",
                "Greetings! I'm here to assist you. What would you like to know?"
            ],
            'weather': [
                "I can help you with weather information! While I don't have real-time data, I can guide you to weather services.",
                "For weather updates, I recommend checking your local weather app or website.",
                "Weather is important! Let me know your location and I can suggest the best weather resources."
            ],
            'music': [
                "I love music! I can help you discover new songs, artists, or genres. What type of music do you enjoy?",
                "Music is wonderful! Tell me about your favorite artists or genres.",
                "Let's talk music! What's your current favorite song or artist?"
            ],
            'general': [
                "That's an interesting question! I'm here to help with various topics.",
                "I understand you said: '{}'. I'm here to help! You can ask me about music, weather, general questions, or just chat.",
                "Thanks for your message! I can assist with many topics. What specifically would you like to know?"
            ]
        }
        
        # Determine intent
        message_lower = message.lower()
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            intent = 'greeting'
        elif any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            intent = 'weather'
        elif any(word in message_lower for word in ['music', 'song', 'artist', 'album']):
            intent = 'music'
        else:
            intent = 'general'
        
        # Get response
        response_templates = responses[intent]
        response = random.choice(response_templates)
        
        # Format response for general intent
        if intent == 'general' and '{}' in response:
            response = response.format(message)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': response,
                'intent': intent,
                'session_id': session_id,
                'timestamp': int(time.time()),
                'status': 'success'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
