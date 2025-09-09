import json
from datetime import datetime

def lambda_handler(event, context):
    try:
        if isinstance(event, dict) and event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': ''
            }
        
        raw_body = event.get('body') if isinstance(event, dict) else None
        try:
            body = json.loads(raw_body) if raw_body else {}
        except Exception:
            body = {}
        message = body.get('message', '')
        
        if not message:
            response_text = 'Hello! I am your voice assistant. How can I help you today?'
        elif 'hello' in message.lower():
            response_text = 'Hello! Nice to meet you. What would you like to know?'
        elif 'weather' in message.lower():
            response_text = 'I would love to help with weather information! This feature is coming soon.'
        elif 'time' in message.lower():
            current_time = datetime.now().strftime('%I:%M %p')
            response_text = f'The current time is {current_time}.'
        else:
            response_text = f'I heard you say: "{message}". I am still learning, but I am here to help!'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'message': response_text,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Sorry, something went wrong. Please try again.'
            })
        }
