"""
Enhanced EventBridge Handler for AI Assistant
Production-grade event-driven processing with EventBridge integration
"""

import json
import boto3
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass, asdict
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Clients
eventbridge = boto3.client('events')
sqs = boto3.client('sqs')
sns = boto3.client('sns')
bedrock = boto3.client('bedrock-runtime')

# Environment Variables
EVENT_BUS_NAME = os.environ.get('EVENTBRIDGE_BUS_NAME', 'ai-assistant-event-bus')
VOICE_QUEUE_URL = os.environ.get('VOICE_PROCESSING_QUEUE_URL', '')
LLM_QUEUE_URL = os.environ.get('LLM_PROCESSING_QUEUE_URL', '')
ANALYTICS_QUEUE_URL = os.environ.get('ANALYTICS_PROCESSING_QUEUE_URL', '')
SYSTEM_ALERTS_TOPIC = os.environ.get('SYSTEM_ALERTS_TOPIC_ARN', '')
USER_ALERTS_TOPIC = os.environ.get('USER_ALERTS_TOPIC_ARN', '')

@dataclass
class UserInteractionEvent:
    """User interaction event structure"""
    user_id: str
    session_id: str
    interaction_type: str  # voice, text, gesture
    message: str
    timestamp: str
    metadata: Dict[str, Any]
    event_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

@dataclass
class AIResponseEvent:
    """AI response event structure"""
    response_id: str
    user_id: str
    session_id: str
    response_type: str  # text, audio, action
    content: str
    confidence: float
    processing_time: float
    ai_model: str
    timestamp: str
    event_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

@dataclass
class SystemErrorEvent:
    """System error event structure"""
    error_id: str
    error_type: str
    error_message: str
    component: str
    severity: str  # low, medium, high, critical
    timestamp: str
    context: Dict[str, Any]
    event_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

class EventBridgeHandler:
    """Enhanced EventBridge handler for AI Assistant"""
    
    def __init__(self):
        self.event_bus_name = EVENT_BUS_NAME
        
    def publish_event(self, source: str, detail_type: str, detail: Dict[str, Any]) -> bool:
        """Publish event to EventBridge"""
        try:
            event_entry = {
                'Source': source,
                'DetailType': detail_type,
                'Detail': json.dumps(detail),
                'EventBusName': self.event_bus_name,
                'Time': datetime.now(timezone.utc)
            }
            
            response = eventbridge.put_events(Entries=[event_entry])
            
            if response['FailedEntryCount'] > 0:
                logger.error(f"Failed to publish event: {response['Entries']}")
                return False
                
            logger.info(f"Successfully published event: {detail_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def publish_user_interaction(self, interaction: UserInteractionEvent) -> bool:
        """Publish user interaction event"""
        return self.publish_event(
            source='ai-assistant',
            detail_type='User Interaction',
            detail=asdict(interaction)
        )
    
    def publish_ai_response(self, response: AIResponseEvent) -> bool:
        """Publish AI response event"""
        return self.publish_event(
            source='ai-assistant',
            detail_type='AI Response Generated',
            detail=asdict(response)
        )
    
    def publish_system_error(self, error: SystemErrorEvent) -> bool:
        """Publish system error event"""
        return self.publish_event(
            source='ai-assistant',
            detail_type='System Error',
            detail=asdict(error)
        )
    
    def publish_session_event(self, user_id: str, session_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish session-related events"""
        session_event = {
            'user_id': user_id,
            'session_id': session_id,
            'event_type': event_type,  # session_start, session_end, session_timeout
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data
        }
        
        return self.publish_event(
            source='ai-assistant',
            detail_type='Session Event',
            detail=session_event
        )

class VoiceAssistantEventProcessor:
    """Main event processor for voice assistant"""
    
    def __init__(self):
        self.eventbridge_handler = EventBridgeHandler()
        
    def process_user_message(self, user_id: str, session_id: str, message: str, 
                           interaction_type: str = 'text', metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user message with EventBridge integration"""
        start_time = time.time()
        
        try:
            # Create user interaction event
            interaction_event = UserInteractionEvent(
                user_id=user_id,
                session_id=session_id,
                interaction_type=interaction_type,
                message=message,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata=metadata or {}
            )
            
            # Publish user interaction event
            self.eventbridge_handler.publish_user_interaction(interaction_event)
            
            # Process the message based on type
            if interaction_type == 'voice':
                response_text = self.process_voice_message(message, user_id, session_id)
            else:
                response_text = self.process_text_message(message, user_id, session_id)
            
            processing_time = time.time() - start_time
            
            # Create AI response event
            response_event = AIResponseEvent(
                response_id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                response_type='text',
                content=response_text,
                confidence=0.95,  # You can implement actual confidence scoring
                processing_time=processing_time,
                ai_model='claude-haiku',
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Publish AI response event
            self.eventbridge_handler.publish_ai_response(response_event)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'response': response_text,
                    'response_id': response_event.response_id,
                    'processing_time': processing_time,
                    'interaction_id': interaction_event.event_id
                })
            }
            
        except Exception as e:
            # Publish error event
            error_event = SystemErrorEvent(
                error_id=str(uuid.uuid4()),
                error_type='ProcessingError',
                error_message=str(e),
                component='VoiceAssistantEventProcessor',
                severity='high',
                timestamp=datetime.now(timezone.utc).isoformat(),
                context={
                    'user_id': user_id,
                    'session_id': session_id,
                    'message': message,
                    'interaction_type': interaction_type
                }
            )
            
            self.eventbridge_handler.publish_system_error(error_event)
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal server error',
                    'error_id': error_event.error_id
                })
            }
    
    def process_text_message(self, message: str, user_id: str, session_id: str) -> str:
        """Process text message with LLM"""
        try:
            # Enhanced prompt for Claude Haiku
            prompt = f"""You are Kairo, an advanced AI assistant. You are helpful, friendly, and knowledgeable.

User: {message}

Respond naturally and helpfully. Keep responses concise but informative."""

            # Call AWS Bedrock Claude Haiku
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return "I'm having trouble processing your request right now. Please try again."
    
    def process_voice_message(self, message: str, user_id: str, session_id: str) -> str:
        """Process voice message (transcribed text)"""
        # Add voice-specific processing logic here
        # For now, treat it the same as text but could add voice-specific features
        return self.process_text_message(message, user_id, session_id)
    
    def handle_sqs_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SQS events from EventBridge"""
        try:
            for record in event.get('Records', []):
                # Parse SQS message
                message_body = json.loads(record['body'])
                
                # Check if it's an EventBridge event
                if 'detail' in message_body:
                    detail = message_body['detail']
                    detail_type = message_body.get('detail-type', '')
                    
                    if detail_type == 'User Interaction':
                        self.handle_user_interaction_event(detail)
                    elif detail_type == 'AI Response Generated':
                        self.handle_ai_response_event(detail)
                    elif detail_type == 'System Error':
                        self.handle_system_error_event(detail)
                
            return {'statusCode': 200, 'body': 'Events processed successfully'}
            
        except Exception as e:
            logger.error(f"Error handling SQS event: {e}")
            return {'statusCode': 500, 'body': f'Error processing events: {str(e)}'}
    
    def handle_user_interaction_event(self, detail: Dict[str, Any]):
        """Handle user interaction events from EventBridge"""
        logger.info(f"Processing user interaction: {detail.get('interaction_type')}")
        
        # Add analytics, logging, or other processing here
        # For example, update user behavior analytics
        
    def handle_ai_response_event(self, detail: Dict[str, Any]):
        """Handle AI response events from EventBridge"""
        logger.info(f"Processing AI response: {detail.get('response_id')}")
        
        # Add response analytics, quality monitoring, etc.
        
    def handle_system_error_event(self, detail: Dict[str, Any]):
        """Handle system error events from EventBridge"""
        logger.error(f"Processing system error: {detail.get('error_type')}")
        
        # Add error handling, alerting, etc.
        if detail.get('severity') in ['high', 'critical']:
            self.send_alert(detail)
    
    def send_alert(self, error_detail: Dict[str, Any]):
        """Send alert for critical errors"""
        try:
            if SYSTEM_ALERTS_TOPIC:
                sns.publish(
                    TopicArn=SYSTEM_ALERTS_TOPIC,
                    Subject=f"Critical Error in AI Assistant: {error_detail.get('error_type')}",
                    Message=json.dumps(error_detail, indent=2)
                )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Main Lambda handler with EventBridge integration"""
    
    processor = VoiceAssistantEventProcessor()
    
    try:
        # Determine event source
        if 'Records' in event:
            # SQS event from EventBridge
            return processor.handle_sqs_event(event)
        
        elif 'httpMethod' in event:
            # API Gateway event
            if event['httpMethod'] == 'POST':
                body = json.loads(event.get('body', '{}'))
                
                user_id = body.get('user_id', 'anonymous')
                session_id = body.get('session_id', str(uuid.uuid4()))
                message = body.get('message', '')
                interaction_type = body.get('interaction_type', 'text')
                metadata = body.get('metadata', {})
                
                if not message:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Message is required'})
                    }
                
                result = processor.process_user_message(
                    user_id, session_id, message, interaction_type, metadata
                )
                
                # Add CORS headers
                if 'headers' not in result:
                    result['headers'] = {}
                result['headers'].update({
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                })
                
                return result
        
        else:
            # Direct EventBridge event
            return processor.handle_sqs_event({'Records': [{'body': json.dumps(event)}]})
            
    except Exception as e:
        logger.error(f"Unhandled error in lambda_handler: {e}")
        
        # Publish error event
        error_event = SystemErrorEvent(
            error_id=str(uuid.uuid4()),
            error_type='LambdaHandlerError',
            error_message=str(e),
            component='lambda_handler',
            severity='critical',
            timestamp=datetime.now(timezone.utc).isoformat(),
            context={'event': event}
        )
        
        processor.eventbridge_handler.publish_system_error(error_event)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'error_id': error_event.error_id
            })
        }
