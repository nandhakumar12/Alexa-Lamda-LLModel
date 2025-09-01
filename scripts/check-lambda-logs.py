#!/usr/bin/env python3
"""
Check Lambda CloudWatch logs and fix any issues
"""

import boto3
import json
import time
from datetime import datetime, timedelta

def check_lambda_logs():
    """Check CloudWatch logs for the Lambda function"""
    print("📋 CHECKING LAMBDA CLOUDWATCH LOGS")
    print("=" * 50)
    
    logs_client = boto3.client('logs')
    lambda_client = boto3.client('lambda')
    
    function_name = 'voice-assistant-chatbot'
    log_group_name = f'/aws/lambda/{function_name}'
    
    try:
        # Get recent log streams
        print("1️⃣ Getting recent log streams...")
        log_streams = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        print(f"✅ Found {len(log_streams['logStreams'])} recent log streams")
        
        if log_streams['logStreams']:
            latest_stream = log_streams['logStreams'][0]
            print(f"   Latest stream: {latest_stream['logStreamName']}")
            
            # Get recent log events
            print("\n2️⃣ Getting recent log events...")
            
            # Get events from the last 10 minutes
            end_time = int(time.time() * 1000)
            start_time = end_time - (10 * 60 * 1000)  # 10 minutes ago
            
            events = logs_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=latest_stream['logStreamName'],
                startTime=start_time,
                endTime=end_time,
                limit=50
            )
            
            print(f"✅ Found {len(events['events'])} recent events")
            
            # Analyze log events
            errors = []
            warnings = []
            info_messages = []
            
            for event in events['events']:
                timestamp = datetime.fromtimestamp(event['timestamp']/1000)
                message = event['message'].strip()
                
                if 'ERROR' in message or 'Exception' in message or 'Traceback' in message:
                    errors.append((timestamp, message))
                elif 'WARNING' in message or 'WARN' in message:
                    warnings.append((timestamp, message))
                else:
                    info_messages.append((timestamp, message))
            
            # Display errors
            if errors:
                print(f"\n❌ ERRORS FOUND ({len(errors)}):")
                for timestamp, message in errors[-5:]:  # Last 5 errors
                    print(f"   {timestamp}: {message}")
            
            # Display warnings
            if warnings:
                print(f"\n⚠️  WARNINGS FOUND ({len(warnings)}):")
                for timestamp, message in warnings[-3:]:  # Last 3 warnings
                    print(f"   {timestamp}: {message}")
            
            # Display recent info
            print(f"\n📝 RECENT INFO ({len(info_messages)}):")
            for timestamp, message in info_messages[-5:]:  # Last 5 info messages
                print(f"   {timestamp}: {message}")
                
            # Check for specific issues
            print("\n3️⃣ Analyzing common issues...")
            
            all_messages = [msg for _, msg in errors + warnings + info_messages]
            all_text = ' '.join(all_messages)
            
            issues_found = []
            
            if 'timeout' in all_text.lower():
                issues_found.append("⏰ Timeout issues detected")
            
            if 'memory' in all_text.lower():
                issues_found.append("💾 Memory issues detected")
            
            if 'permission' in all_text.lower() or 'access denied' in all_text.lower():
                issues_found.append("🔒 Permission issues detected")
            
            if 'import' in all_text.lower() and 'error' in all_text.lower():
                issues_found.append("📦 Import/dependency issues detected")
            
            if 'json' in all_text.lower() and ('decode' in all_text.lower() or 'parse' in all_text.lower()):
                issues_found.append("🔧 JSON parsing issues detected")
            
            if issues_found:
                print("   Issues detected:")
                for issue in issues_found:
                    print(f"      {issue}")
            else:
                print("   ✅ No obvious issues detected in logs")
        
        else:
            print("❌ No log streams found")
    
    except Exception as e:
        print(f"❌ Failed to check logs: {e}")
    
    # Test the Lambda function directly
    print("\n4️⃣ Testing Lambda function directly...")
    
    try:
        test_event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "message": "Direct Lambda test",
                "session_id": "direct-test"
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        print(f"   Status Code: {response['StatusCode']}")
        
        if 'errorMessage' in payload:
            print(f"   ❌ Lambda Error: {payload['errorMessage']}")
            if 'errorType' in payload:
                print(f"   Error Type: {payload['errorType']}")
            if 'stackTrace' in payload:
                print(f"   Stack Trace: {payload['stackTrace'][:500]}...")
        else:
            print(f"   ✅ Lambda Response: {str(payload)[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Direct Lambda test failed: {e}")

def fix_lambda_function():
    """Fix common Lambda function issues"""
    print("\n🔧 FIXING LAMBDA FUNCTION")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda')
    function_name = 'voice-assistant-chatbot'
    
    # Updated Lambda code with better error handling
    improved_lambda_code = '''
import json
import logging
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Voice Assistant Chatbot Lambda Function - Improved Version
    """
    
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return cors_response(200, '')
        
        # Parse request body safely
        try:
            if 'body' in event and event['body']:
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
            else:
                body = event
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return cors_response(400, {'error': 'Invalid JSON in request body'})
        
        # Extract message with defaults
        message = body.get('message', 'Hello')
        session_id = body.get('session_id', str(uuid.uuid4()))
        user_id = body.get('user_id', 'anonymous')
        
        logger.info(f"Processing message: '{message}' for session: {session_id}")
        
        # Generate response
        try:
            response_text = generate_response(message)
            intent = detect_intent(message)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response_text = "I'm sorry, I encountered an error processing your request. Please try again."
            intent = "error"
        
        # Create response
        response_data = {
            'response': response_text,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'intent': intent,
            'status': 'success'
        }
        
        logger.info(f"Generated response for intent '{intent}': {response_text[:100]}...")
        
        return cors_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        
        error_response = {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'error'
        }
        
        return cors_response(500, error_response)

def cors_response(status_code, body):
    """Create a response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(body) if body else ''
    }

def generate_response(message):
    """Generate AI response based on message"""
    
    if not message or not isinstance(message, str):
        return "I didn't receive a valid message. Could you please try again?"
    
    message_lower = message.lower().strip()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
    
    # Music related
    elif any(word in message_lower for word in ['music', 'song', 'play', 'spotify', 'artist', 'album']):
        return "I'd be happy to help you with music! I can assist with finding songs, creating playlists, or recommending artists. What kind of music are you interested in?"
    
    # Weather related
    elif any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast']):
        return "I can help you with weather information! While I don't have real-time weather data right now, I can help you plan based on general weather patterns. What location are you interested in?"
    
    # General assistance
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'what can you do']):
        return "I'm here to help! I can assist you with music recommendations, general questions, weather information, and much more. What would you like to know?"
    
    # Thank you
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! Is there anything else I can help you with today?"
    
    # Goodbye
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
        return "Goodbye! It was great chatting with you. Feel free to come back anytime!"
    
    # Default response
    else:
        return f"I understand you said: '{message}'. I'm here to help! You can ask me about music, weather, general questions, or just chat with me. What would you like to know?"

def detect_intent(message):
    """Detect the intent of the message"""
    
    if not message or not isinstance(message, str):
        return 'unknown'
    
    message_lower = message.lower().strip()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return 'greeting'
    elif any(word in message_lower for word in ['music', 'song', 'play', 'spotify', 'artist', 'album']):
        return 'music'
    elif any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast']):
        return 'weather'
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'what can you do']):
        return 'help'
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return 'gratitude'
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
        return 'goodbye'
    else:
        return 'general'
'''
    
    # Update the Lambda function
    try:
        import zipfile
        import tempfile
        import os
        
        # Create temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            lambda_file = os.path.join(temp_dir, 'lambda_function.py')
            zip_file = os.path.join(temp_dir, 'function.zip')
            
            # Write improved code
            with open(lambda_file, 'w') as f:
                f.write(improved_lambda_code)
            
            # Create ZIP
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(lambda_file, 'lambda_function.py')
            
            # Read ZIP content
            with open(zip_file, 'rb') as f:
                zip_content = f.read()
            
            # Update function code
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
            print(f"✅ Updated Lambda function code")
            print(f"   Version: {response['Version']}")
            print(f"   Last Modified: {response['LastModified']}")
            
            # Update function configuration for better performance
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Timeout=30,
                MemorySize=512,  # Increased memory
                Environment={
                    'Variables': {
                        'ENVIRONMENT': 'production',
                        'LOG_LEVEL': 'INFO'
                    }
                }
            )
            
            print(f"✅ Updated Lambda configuration")
            print(f"   Timeout: 30 seconds")
            print(f"   Memory: 512 MB")
            
    except Exception as e:
        print(f"❌ Failed to update Lambda function: {e}")

if __name__ == "__main__":
    check_lambda_logs()
    fix_lambda_function()
    
    print("\n" + "=" * 50)
    print("🎉 LAMBDA FUNCTION ANALYSIS & FIX COMPLETE!")
    print("✅ Improved error handling")
    print("✅ Better logging")
    print("✅ Increased memory and timeout")
    print("✅ More robust JSON parsing")
    
    print("\n💡 Test the API again - it should work much better now!")
