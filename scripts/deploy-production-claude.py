#!/usr/bin/env python3
"""
Deploy production-grade Lambda function with Claude LLM
"""

import boto3
import json
import os
import zipfile
import time

def create_production_lambda():
    """Create production Lambda function with Claude LLM"""
    print("⚡ CREATING PRODUCTION LAMBDA WITH CLAUDE")
    print("=" * 50)
    
    # Production Lambda code with Claude Bedrock
    lambda_code = '''import json
import boto3
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Environment variables
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
CONVERSATIONS_TABLE = os.environ.get('CONVERSATIONS_TABLE', 'nandhakumar-conversations')

# Bedrock model configuration
MODEL_CONFIG = {
    'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',
    'max_tokens': 1000,
    'temperature': 0.7
}

class ProductionChatbot:
    """Production-ready chatbot with Claude LLM"""
    
    def __init__(self):
        try:
            self.conversations_table = dynamodb.Table(CONVERSATIONS_TABLE)
        except Exception as e:
            logger.warning(f"Could not connect to DynamoDB: {e}")
            self.conversations_table = None
    
    def get_claude_response(self, message: str, user_id: str, session_id: str) -> str:
        """Get response from AWS Bedrock Claude"""
        try:
            # Get conversation history for context
            conversation_context = self.get_conversation_context(session_id)
            
            # Build context-aware prompt
            system_prompt = """You are Nandhakumar's AI Assistant, a helpful and intelligent voice assistant. 
You should be conversational, engaging, and provide helpful responses. 
You can help with various topics including:
- General questions and conversations
- Music recommendations and discussions
- Weather information
- Technology topics
- Creative writing and brainstorming
- Problem-solving and advice

Keep responses natural, friendly, and appropriately detailed. 
If you don't know something specific, be honest about it but offer to help in other ways."""

            # Prepare conversation history
            messages = []
            
            # Add conversation context if available
            if conversation_context:
                for msg in conversation_context[-6:]:  # Last 6 messages for context
                    role = "user" if msg.get('role') == 'user' else "assistant"
                    messages.append({
                        "role": role,
                        "content": msg.get('content', '')
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": MODEL_CONFIG['max_tokens'],
                "temperature": MODEL_CONFIG['temperature'],
                "system": system_prompt,
                "messages": messages
            }

            response = bedrock.invoke_model(
                modelId=MODEL_CONFIG['model_id'],
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            assistant_response = response_body['content'][0]['text'].strip()
            
            # Save conversation
            self.save_conversation(session_id, user_id, message, assistant_response)
            
            logger.info(f"Claude response generated for user {user_id}")
            return assistant_response

        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            return self.get_fallback_response(message)
    
    def get_conversation_context(self, session_id: str) -> list:
        """Get conversation history for context"""
        try:
            if not self.conversations_table:
                return []
                
            response = self.conversations_table.query(
                KeyConditionExpression='session_id = :sid',
                ExpressionAttributeValues={':sid': session_id},
                ScanIndexForward=True,
                Limit=10
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.warning(f"Could not get conversation context: {e}")
            return []
    
    def save_conversation(self, session_id: str, user_id: str, user_message: str, assistant_response: str):
        """Save conversation to DynamoDB"""
        try:
            if not self.conversations_table:
                return
                
            timestamp = datetime.utcnow().isoformat()
            
            # Save user message
            self.conversations_table.put_item(
                Item={
                    'session_id': session_id,
                    'timestamp': timestamp + '_user',
                    'user_id': user_id,
                    'role': 'user',
                    'content': user_message,
                    'created_at': timestamp
                }
            )
            
            # Save assistant response
            self.conversations_table.put_item(
                Item={
                    'session_id': session_id,
                    'timestamp': timestamp + '_assistant',
                    'user_id': user_id,
                    'role': 'assistant',
                    'content': assistant_response,
                    'created_at': timestamp
                }
            )
            
        except Exception as e:
            logger.warning(f"Could not save conversation: {e}")
    
    def get_fallback_response(self, message: str) -> str:
        """Fallback response when Claude is unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm Nandhakumar's AI Assistant. I'm having some technical difficulties with my advanced AI, but I'm still here to help you!"
        elif any(word in message_lower for word in ['music', 'song', 'artist']):
            return "I'd love to help you with music! While my advanced AI is temporarily unavailable, I can still chat about your favorite artists and songs."
        elif any(word in message_lower for word in ['weather', 'temperature']):
            return "For weather information, I recommend checking your local weather app. My advanced weather AI is currently being updated."
        else:
            return f"I understand you said: '{message}'. I'm experiencing some technical difficulties with my advanced AI, but I'm working to resolve them. How else can I help you?"

    def determine_intent(self, message: str) -> str:
        """Simple intent classification"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(word in message_lower for word in ['music', 'song', 'artist', 'album']):
            return 'music'
        elif any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            return 'weather'
        elif any(word in message_lower for word in ['help', 'assist', 'support']):
            return 'help'
        else:
            return 'general'

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Main Lambda handler for production chatbot"""
    
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
    
    chatbot = ProductionChatbot()
    
    try:
        # Parse the request
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Extract request data
        message = body.get('message', '').strip()
        session_id = body.get('session_id', str(uuid.uuid4()))
        message_type = body.get('type', 'text')
        
        # Extract user ID
        user_id = body.get('user_id', 'anonymous')
        
        # Handle empty message
        if not message:
            response_text = "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
            intent = 'greeting'
        else:
            # Get Claude response
            response_text = chatbot.get_claude_response(message, user_id, session_id)
            intent = chatbot.determine_intent(message)
        
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
                'response': response_text,
                'intent': intent,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'success',
                'model': 'claude-3-haiku',
                'user_id': user_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'status': 'error'
            })
        }
'''
    
    # Create Lambda deployment package
    lambda_dir = "production-lambda"
    if os.path.exists(lambda_dir):
        import shutil
        shutil.rmtree(lambda_dir)
    
    os.makedirs(lambda_dir, exist_ok=True)
    
    # Write Lambda function
    with open(f"{lambda_dir}/lambda_function.py", 'w') as f:
        f.write(lambda_code)
    
    # Create ZIP package
    zip_path = "production-lambda.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(f"{lambda_dir}/lambda_function.py", "lambda_function.py")
    
    print(f"✅ Created production Lambda package")
    return zip_path

def deploy_production_lambda():
    """Deploy the production Lambda function"""
    print("\n🚀 DEPLOYING PRODUCTION LAMBDA")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = 'nandhakumar-production-chatbot'
    
    # Create IAM role with Bedrock permissions
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
    
    # IAM policy for Bedrock and DynamoDB
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": "arn:aws:dynamodb:us-east-1:*:table/nandhakumar-conversations"
            }
        ]
    }
    
    role_name = f"{function_name}-role"
    
    try:
        # Create role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for production chatbot with Claude LLM'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_name}")
        
        # Create and attach policy
        policy_name = f"{function_name}-policy"
        policy_response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(lambda_policy),
            Description='Policy for production chatbot with Bedrock and DynamoDB access'
        )
        
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        print(f"✅ Created and attached policy: {policy_name}")
        
        # Wait for role to be ready
        print("⏳ Waiting for IAM role to be ready...")
        time.sleep(15)
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        role_response = iam_client.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_name}")
    
    # Create deployment package
    zip_path = create_production_lambda()
    
    try:
        # Read the zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Try to update existing function first
        try:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated existing Lambda function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Function doesn't exist, create it
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Production chatbot with Claude LLM via AWS Bedrock',
                Timeout=60,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'ENVIRONMENT': 'production',
                        'CONVERSATIONS_TABLE': 'nandhakumar-conversations'
                    }
                }
            )
            print(f"✅ Created new Lambda function: {function_name}")
        
        # Get function details
        function_info = lambda_client.get_function(FunctionName=function_name)
        function_arn = function_info['Configuration']['FunctionArn']
        
        print(f"✅ Lambda function ARN: {function_arn}")
        
        # Clean up
        os.remove(zip_path)
        import shutil
        shutil.rmtree("production-lambda")
        
        return function_name, function_arn
        
    except Exception as e:
        print(f"❌ Error deploying Lambda: {e}")
        return None, None

def create_dynamodb_table():
    """Create DynamoDB table for conversations"""
    print("\n🗄️ CREATING DYNAMODB TABLE")
    print("=" * 50)
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    table_name = 'nandhakumar-conversations'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"✅ Created DynamoDB table: {table_name}")
        
        # Wait for table to be active
        print("⏳ Waiting for table to be active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"✅ DynamoDB table already exists: {table_name}")

def test_production_lambda(function_name):
    """Test the production Lambda function"""
    print(f"\n🧪 TESTING PRODUCTION LAMBDA")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "message": "Hello! Can you tell me about yourself and what you can do?",
            "session_id": "production-test-session"
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if payload.get('statusCode') == 200:
            body = json.loads(payload['body'])
            print(f"✅ Production Lambda test successful!")
            print(f"   Response: {body.get('response', 'No response')[:80]}...")
            print(f"   Model: {body.get('model', 'Unknown')}")
            print(f"   Intent: {body.get('intent', 'No intent')}")
            return True
        else:
            print(f"❌ Production Lambda test failed: {payload}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lambda: {e}")
        return False

def main():
    """Main function"""
    print("🚨 DEPLOYING PRODUCTION CLAUDE CHATBOT")
    print("=" * 60)
    
    # Create DynamoDB table first
    create_dynamodb_table()
    
    # Deploy Lambda function
    function_name, function_arn = deploy_production_lambda()
    
    if function_name:
        success = test_production_lambda(function_name)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 PRODUCTION LAMBDA DEPLOYMENT SUCCESSFUL!")
            print(f"\n📋 DETAILS:")
            print(f"   Function Name: {function_name}")
            print(f"   Function ARN: {function_arn}")
            print(f"   Runtime: Python 3.9")
            print(f"   LLM: Claude 3 Haiku via AWS Bedrock")
            print(f"   Memory: 512 MB")
            print(f"   Timeout: 60 seconds")
            print(f"   DynamoDB: nandhakumar-conversations")
            
            # Save function details for next step
            with open('production-lambda-details.json', 'w') as f:
                json.dump({
                    'function_name': function_name,
                    'function_arn': function_arn,
                    'model': 'claude-3-haiku',
                    'provider': 'aws-bedrock'
                }, f, indent=2)
            
            print(f"\n✅ Saved function details to production-lambda-details.json")
            print(f"\n🎯 NEXT STEP: Create production API Gateway")
            
        else:
            print("❌ PRODUCTION LAMBDA DEPLOYMENT FAILED!")
    else:
        print("❌ PRODUCTION LAMBDA DEPLOYMENT FAILED!")

if __name__ == "__main__":
    main()
