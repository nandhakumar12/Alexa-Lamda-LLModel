import json
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
CONVERSATIONS_TABLE = os.environ.get('CONVERSATIONS_TABLE', 'voice-assistant-ai-prod-conversations')

# Bedrock model configuration
MODEL_CONFIG = {
    'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',
    'max_tokens': 1000,
    'temperature': 0.7
}

class ProductionChatbot:
    """Production-ready chatbot with proper error handling and fallbacks"""
    
    def __init__(self):
        try:
            self.conversations_table = dynamodb.Table(CONVERSATIONS_TABLE)
        except Exception as e:
            logger.warning(f"Could not connect to DynamoDB: {e}")
            self.conversations_table = None
    
    def get_llm_response(self, message: str, user_id: str) -> str:
        """Get response from AWS Bedrock Claude"""
        try:
            # Create a conversational prompt
            prompt = f"""You are Nandhakumar's AI Assistant, a helpful and friendly voice assistant. 
You should be conversational, helpful, and engaging. Keep responses concise but informative.

User: {message}
Assistant:"""

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": MODEL_CONFIG['max_tokens'],
                "temperature": MODEL_CONFIG['temperature'],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = bedrock.invoke_model(
                modelId=MODEL_CONFIG['model_id'],
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            assistant_response = response_body['content'][0]['text'].strip()
            
            logger.info(f"LLM response generated for user {user_id}")
            return assistant_response

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self.get_fallback_response(message)
    
    def get_fallback_response(self, message: str) -> str:
        """Provide intelligent fallback responses when LLM is unavailable"""
        message_lower = message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
        
        # How are you responses
        elif any(phrase in message_lower for phrase in ['how are you', 'how do you do', 'how\'s it going']):
            return "I'm doing great, thank you for asking! I'm here and ready to help you with anything you need."
        
        # Capability questions
        elif any(phrase in message_lower for phrase in ['what can you do', 'what are you capable of', 'help me', 'what do you know']):
            return "I can help you with conversations, answer questions, provide information, and assist with various tasks. What would you like to explore?"
        
        # Time and date
        elif 'time' in message_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        elif 'date' in message_lower:
            return f"Today's date is {datetime.now().strftime('%B %d, %Y')}."
        
        # About Nandhakumar
        elif 'nandhakumar' in message_lower:
            return "Nandhakumar is the creator of this AI assistant! He built this using modern AWS services and AI technology to provide you with an intelligent conversational experience."
        
        # Thank you responses
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're very welcome! I'm happy to help. Is there anything else you'd like to know or do?"
        
        # Goodbye responses
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            return "Goodbye! It was great talking with you. Feel free to come back anytime you need assistance!"
        
        # Default response
        else:
            return "I understand you're asking about something. Could you please rephrase your question or try asking something else? I'm here to help!"
    
    def save_conversation(self, user_id: str, user_message: str, bot_response: str, session_id: str):
        """Save conversation to DynamoDB for analytics"""
        if not self.conversations_table:
            return
        
        try:
            conversation_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            self.conversations_table.put_item(
                Item={
                    'conversation_id': conversation_id,
                    'user_id': user_id,
                    'session_id': session_id,
                    'timestamp': timestamp,
                    'user_message': user_message,
                    'bot_response': bot_response,
                    'response_type': 'llm' if 'I understand you\'re asking' not in bot_response else 'fallback'
                }
            )
            logger.info(f"Conversation saved: {conversation_id}")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Main Lambda handler for production chatbot"""
    
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
        
        # Extract user ID from JWT claims (set by API Gateway authorizer)
        user_id = 'anonymous'
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            claims = event['requestContext']['authorizer'].get('claims', {})
            user_id = claims.get('sub', claims.get('username', 'anonymous'))
        
        # Handle empty message (welcome message)
        if not message:
            response_text = "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?"
        else:
            # Get response from LLM with fallback
            response_text = chatbot.get_llm_response(message, user_id)
        
        # Save conversation for analytics
        if message:  # Don't save welcome messages
            chatbot.save_conversation(user_id, message, response_text, session_id)
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'response': response_text,
                'session_id': session_id,
                'conversation_id': str(uuid.uuid4()),
                'intent': 'general_conversation',
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f"Error in chatbot handler: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'I apologize, but I encountered an error. Please try again.',
                'message': 'Internal server error'
            })
        }
