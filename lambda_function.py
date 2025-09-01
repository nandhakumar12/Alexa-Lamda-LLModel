import json
import requests
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Production Lambda function for Nandhakumar's AI Assistant
    """
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

        # Get Claude API key from environment
        claude_api_key = os.environ.get('CLAUDE_API_KEY')
        if claude_api_key and claude_api_key != 'YOUR_CLAUDE_API_KEY_HERE':
            response_text = get_claude_response(user_message, user_name, claude_api_key)
        else:
            response_text = get_intelligent_response(user_message, user_name)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'user': user_name,
                'model': 'claude-3-sonnet' if claude_api_key else 'nandhakumar-ai'
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_claude_response(message, user_name, api_key):
    """Get response from Claude 3"""
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "system": f"You are {user_name}'s personal AI assistant. Be helpful, friendly, and engaging. Always greet {user_name} warmly.",
            "messages": [{"role": "user", "content": message}]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            print(f"Claude API error: {response.status_code}")
            return get_intelligent_response(message, user_name)

    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return get_intelligent_response(message, user_name)

def get_intelligent_response(message, user_name):
    """Generate intelligent responses based on message content"""
    message_lower = message.lower()

    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return f"Hello {user_name}! I'm your personal AI assistant. I'm excited to help you today! How can I assist you?"

    # Music-related responses
    elif any(word in message_lower for word in ['music', 'song', 'artist', 'album', 'spotify', 'playlist', 'listen']):
        return f"Hi {user_name}! I'd love to talk about music with you! 🎵 I can help you discover new artists, discuss different genres, or chat about your favorite songs. What kind of music are you into?"

    # Technology responses
    elif any(word in message_lower for word in ['technology', 'tech', 'coding', 'programming', 'ai', 'machine learning', 'aws', 'cloud']):
        return f"Great question about technology, {user_name}! 💻 I'm passionate about tech topics. I can discuss programming, cloud computing, AI developments, and more. What specific technology interests you?"

    # Personal questions
    elif any(phrase in message_lower for phrase in ['who are you', 'what are you', 'tell me about yourself']):
        return f"I'm {user_name}'s personal AI assistant! 🤖 I'm designed to be helpful, knowledgeable, and friendly. I can assist with various tasks, answer questions, and have engaging conversations. How can I help you today?"

    # Help requests
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'can you']):
        return f"Of course, {user_name}! I'm here to help. 🚀 I can assist with answering questions, discussing topics, providing information, or just having a friendly conversation. What would you like help with?"

    # Weather
    elif 'weather' in message_lower:
        return f"I'd love to help with weather information, {user_name}! ☀️ While I don't have real-time weather access right now, I recommend checking your local weather app. Is there anything else I can help you with?"

    # Time/date
    elif any(word in message_lower for word in ['time', 'date', 'today']):
        return f"Hi {user_name}! I can help with time-related questions. What would you like to know or discuss about today?"

    # Compliments
    elif any(word in message_lower for word in ['good', 'great', 'awesome', 'amazing', 'excellent']):
        return f"Thank you so much, {user_name}! 😊 That really means a lot to me. I'm here to provide the best assistance possible. What can I help you with today?"

    # General conversation
    else:
        responses = [
            f"That's really interesting, {user_name}! You mentioned '{message}'. I'd love to learn more about your thoughts on this. Could you tell me more?",
            f"Great point, {user_name}! '{message}' sounds fascinating. What aspects of this interest you most?",
            f"Thanks for sharing that, {user_name}! '{message}' is definitely worth discussing. What's your perspective on this?",
            f"I appreciate you bringing that up, {user_name}! '{message}' - that's something I'd like to explore further with you. What would you like to discuss about it?"
        ]
        import random
        return random.choice(responses)
