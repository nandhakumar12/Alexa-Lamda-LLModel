#!/usr/bin/env python3
"""
Create a completely fresh Voice Assistant AI system from scratch
"""

import os
import shutil
import boto3
import json
import time

def cleanup_old_system():
    """Clean up old conflicting files"""
    print("🧹 CLEANING UP OLD SYSTEM")
    print("=" * 50)
    
    # Backup important files first
    backup_dir = f"backup-{int(time.time())}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    backup_files = [
        "frontend/.env",
        "backend/lambda_functions/chatbot/lambda_function.py"
    ]
    
    for file_path in backup_files:
        if os.path.exists(file_path):
            try:
                dest = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(file_path, dest)
                print(f"✅ Backed up: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not backup {file_path}: {e}")
    
    # Clean up S3 bucket
    print("\n🗑️  Cleaning S3 bucket...")
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    try:
        # List and delete all objects
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            delete_objects = [{'Key': obj['Key']} for obj in objects['Contents']]
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_objects}
            )
            print(f"✅ Deleted {len(delete_objects)} files from S3")
        else:
            print("✅ S3 bucket already empty")
    except Exception as e:
        print(f"⚠️  S3 cleanup error: {e}")
    
    print(f"✅ Cleanup complete! Backup saved in: {backup_dir}")

def create_fresh_frontend():
    """Create a fresh frontend without authentication"""
    print("\n🎨 CREATING FRESH FRONTEND")
    print("=" * 50)
    
    # Create new frontend directory
    fresh_frontend_dir = "fresh-frontend"
    if os.path.exists(fresh_frontend_dir):
        shutil.rmtree(fresh_frontend_dir)
    
    os.makedirs(fresh_frontend_dir, exist_ok=True)
    
    # Create package.json
    package_json = {
        "name": "nandhakumar-voice-assistant",
        "version": "1.0.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1",
            "axios": "^1.6.0",
            "react-router-dom": "^6.8.0",
            "react-hot-toast": "^2.4.1"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
        },
        "eslintConfig": {
            "extends": [
                "react-app",
                "react-app/jest"
            ]
        },
        "browserslist": {
            "production": [
                ">0.2%",
                "not dead",
                "not op_mini all"
            ],
            "development": [
                "last 1 chrome version",
                "last 1 firefox version",
                "last 1 safari version"
            ]
        }
    }
    
    with open(f"{fresh_frontend_dir}/package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create public directory
    public_dir = f"{fresh_frontend_dir}/public"
    os.makedirs(public_dir, exist_ok=True)
    
    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Nandhakumar's AI Voice Assistant" />
    <title>Nandhakumar's AI Assistant</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
    
    with open(f"{public_dir}/index.html", 'w') as f:
        f.write(index_html)
    
    # Create src directory
    src_dir = f"{fresh_frontend_dir}/src"
    os.makedirs(src_dir, exist_ok=True)
    
    print(f"✅ Created fresh frontend structure in: {fresh_frontend_dir}")

def create_simple_lambda():
    """Create a simple Lambda function"""
    print("\n⚡ CREATING SIMPLE LAMBDA FUNCTION")
    print("=" * 50)
    
    lambda_dir = "fresh-lambda"
    if os.path.exists(lambda_dir):
        shutil.rmtree(lambda_dir)
    
    os.makedirs(lambda_dir, exist_ok=True)
    
    # Create simple lambda function
    lambda_code = '''import json
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
'''
    
    with open(f"{lambda_dir}/lambda_function.py", 'w') as f:
        f.write(lambda_code)
    
    print(f"✅ Created simple Lambda function in: {lambda_dir}")

def main():
    """Main function"""
    print("🚨 CREATING FRESH VOICE ASSISTANT AI SYSTEM")
    print("=" * 60)
    
    cleanup_old_system()
    create_fresh_frontend()
    create_simple_lambda()
    
    print("\n" + "=" * 60)
    print("🎉 FRESH SYSTEM STRUCTURE CREATED!")
    
    print(f"\n📁 CREATED:")
    print(f"   📂 fresh-frontend/ - Clean React app")
    print(f"   📂 fresh-lambda/ - Simple Lambda function")
    print(f"   📂 backup-{int(time.time())}/ - Backup of old files")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Build the React components")
    print(f"   2. Deploy the Lambda function")
    print(f"   3. Create new API Gateway")
    print(f"   4. Deploy and test")
    
    print(f"\n💡 NO AUTHENTICATION - DIRECT ACCESS TO CHATBOT!")

if __name__ == "__main__":
    main()
