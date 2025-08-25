"""
Voice Assistant AI - Chatbot Handler Lambda Function
Handles voice and text interactions with Amazon Lex and Alexa Skills Kit
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

# Import shared utilities
import sys
sys.path.append('/opt/python')
sys.path.append('.')

try:
    from shared.logger import get_logger
    from shared.db import DynamoDBClient
    from shared.s3 import S3Client
except ImportError:
    # Fallback for local development
    pass

# Initialize AWS Lambda Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
lex_client = boto3.client('lexv2-runtime')
s3_client = boto3.client('s3')

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
LEX_BOT_ID = os.environ.get('LEX_BOT_ID')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

# Constants
LEX_BOT_ALIAS_ID = 'TSTALIASID'  # Test alias for development
LEX_LOCALE_ID = 'en_US'


class VoiceAssistantChatbot:
    """Main chatbot class for handling voice and text interactions"""
    
    def __init__(self):
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        self.lex_client = lex_client
        self.s3_client = s3_client
    
    @tracer.capture_method
    def process_text_message(self, user_id: str, message: str, session_id: str) -> Dict[str, Any]:
        """Process text message through Amazon Lex"""
        try:
            # Call Amazon Lex
            response = self.lex_client.recognize_text(
                botId=LEX_BOT_ID,
                botAliasId=LEX_BOT_ALIAS_ID,
                localeId=LEX_LOCALE_ID,
                sessionId=session_id,
                text=message
            )
            
            # Extract response
            bot_response = response.get('messages', [{}])[0].get('content', 'I apologize, but I didn\'t understand that.')
            intent_name = response.get('sessionState', {}).get('intent', {}).get('name', 'Unknown')
            
            # Store conversation in DynamoDB
            conversation_data = {
                'user_id': user_id,
                'conversation_id': str(uuid.uuid4()),
                'session_id': session_id,
                'timestamp': int(datetime.now(timezone.utc).timestamp()),
                'user_message': message,
                'bot_response': bot_response,
                'intent_name': intent_name,
                'message_type': 'text',
                'environment': ENVIRONMENT
            }
            
            self.table.put_item(Item=conversation_data)
            
            # Emit custom metrics
            metrics.add_metric(name="TextMessageProcessed", unit=MetricUnit.Count, value=1)
            metrics.add_metadata(key="intent", value=intent_name)
            
            return {
                'response': bot_response,
                'intent': intent_name,
                'session_id': session_id,
                'conversation_id': conversation_data['conversation_id']
            }
            
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")
            metrics.add_metric(name="TextMessageError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def process_voice_message(self, user_id: str, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Process voice message through Amazon Lex"""
        try:
            # Store audio file in S3
            audio_key = f"audio/{user_id}/{session_id}/{uuid.uuid4()}.wav"
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=audio_key,
                Body=audio_data,
                ContentType='audio/wav'
            )
            
            # Call Amazon Lex with audio
            response = self.lex_client.recognize_utterance(
                botId=LEX_BOT_ID,
                botAliasId=LEX_BOT_ALIAS_ID,
                localeId=LEX_LOCALE_ID,
                sessionId=session_id,
                requestContentType='audio/l16; rate=16000; channels=1',
                inputStream=audio_data
            )
            
            # Extract response
            bot_response = response.get('messages', [{}])[0].get('content', 'I apologize, but I didn\'t understand that.')
            intent_name = response.get('sessionState', {}).get('intent', {}).get('name', 'Unknown')
            
            # Store conversation in DynamoDB
            conversation_data = {
                'user_id': user_id,
                'conversation_id': str(uuid.uuid4()),
                'session_id': session_id,
                'timestamp': int(datetime.now(timezone.utc).timestamp()),
                'audio_s3_key': audio_key,
                'bot_response': bot_response,
                'intent_name': intent_name,
                'message_type': 'voice',
                'environment': ENVIRONMENT
            }
            
            self.table.put_item(Item=conversation_data)
            
            # Emit custom metrics
            metrics.add_metric(name="VoiceMessageProcessed", unit=MetricUnit.Count, value=1)
            metrics.add_metadata(key="intent", value=intent_name)
            
            return {
                'response': bot_response,
                'intent': intent_name,
                'session_id': session_id,
                'conversation_id': conversation_data['conversation_id'],
                'audio_url': f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{audio_key}"
            }
            
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            metrics.add_metric(name="VoiceMessageError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def process_alexa_request(self, alexa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process Alexa Skills Kit request"""
        try:
            request_type = alexa_request.get('request', {}).get('type')
            user_id = alexa_request.get('session', {}).get('user', {}).get('userId', 'anonymous')
            session_id = alexa_request.get('session', {}).get('sessionId', str(uuid.uuid4()))
            
            if request_type == 'LaunchRequest':
                response_text = "Welcome to Voice Assistant AI! How can I help you today?"
                
            elif request_type == 'IntentRequest':
                intent_name = alexa_request.get('request', {}).get('intent', {}).get('name')
                slots = alexa_request.get('request', {}).get('intent', {}).get('slots', {})
                
                # Extract slot values
                slot_values = {}
                for slot_name, slot_data in slots.items():
                    if slot_data.get('value'):
                        slot_values[slot_name] = slot_data['value']
                
                # Process through Lex for consistent handling
                user_message = f"Intent: {intent_name}"
                if slot_values:
                    user_message += f" with slots: {json.dumps(slot_values)}"
                
                lex_response = self.process_text_message(user_id, user_message, session_id)
                response_text = lex_response['response']
                
            elif request_type == 'SessionEndedRequest':
                response_text = "Goodbye! Thank you for using Voice Assistant AI."
                
            else:
                response_text = "I'm sorry, I didn't understand that request."
            
            # Build Alexa response
            alexa_response = {
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': response_text
                    },
                    'shouldEndSession': request_type == 'SessionEndedRequest'
                }
            }
            
            # Emit custom metrics
            metrics.add_metric(name="AlexaRequestProcessed", unit=MetricUnit.Count, value=1)
            metrics.add_metadata(key="request_type", value=request_type)
            
            return alexa_response
            
        except Exception as e:
            logger.error(f"Error processing Alexa request: {str(e)}")
            metrics.add_metric(name="AlexaRequestError", unit=MetricUnit.Count, value=1)
            raise


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Main Lambda handler for chatbot functionality"""
    
    try:
        logger.info("Processing chatbot request", extra={"event": event})
        
        # Initialize chatbot
        chatbot = VoiceAssistantChatbot()
        
        # Determine request type
        if 'httpMethod' in event:
            # API Gateway request
            http_method = event['httpMethod']
            path = event.get('path', '')
            body = json.loads(event.get('body', '{}'))
            
            # Extract user information
            user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'anonymous')
            session_id = body.get('session_id', str(uuid.uuid4()))
            
            if path.endswith('/alexa') and http_method == 'POST':
                # Alexa Skills Kit request
                response = chatbot.process_alexa_request(body)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(response)
                }
            
            elif http_method == 'POST':
                # Regular chatbot request
                message_type = body.get('type', 'text')
                
                if message_type == 'text':
                    message = body.get('message', '')
                    response = chatbot.process_text_message(user_id, message, session_id)
                    
                elif message_type == 'voice':
                    # Audio data should be base64 encoded
                    import base64
                    audio_data = base64.b64decode(body.get('audio_data', ''))
                    response = chatbot.process_voice_message(user_id, audio_data, session_id)
                    
                else:
                    raise ValueError(f"Unsupported message type: {message_type}")
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(response)
                }
            
            else:
                return {
                    'statusCode': 405,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Method not allowed'})
                }
        
        else:
            # Direct Lambda invocation or other event sources
            logger.info("Direct Lambda invocation")
            return {'statusCode': 200, 'body': 'Chatbot handler is running'}
    
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        metrics.add_metric(name="LambdaHandlerError", unit=MetricUnit.Count, value=1)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e) if ENVIRONMENT != 'prod' else 'An error occurred'
            })
        }
