# 💻 Voice Assistant AI - Coding Interview Questions

Practical coding questions based on the Voice Assistant AI project. These questions test implementation skills and problem-solving abilities.

## 🐍 Python/Lambda Coding Questions

### Question 1: Lambda Function Error Handling
**Scenario**: Write a robust Lambda function that processes voice messages with proper error handling.

```python
import json
import boto3
import logging
from typing import Dict, Any, Optional

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process voice message with error handling
    
    Expected Implementation:
    - Parse and validate input
    - Handle different error scenarios
    - Return proper HTTP responses
    - Log errors appropriately
    """
    # Your implementation here
    pass

# Test cases to handle:
# 1. Missing required fields
# 2. Invalid audio format
# 3. DynamoDB connection errors
# 4. Lex service unavailable
# 5. S3 upload failures
```

**Expected Solution**:
```python
import json
import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
lex_client = boto3.client('lexv2-runtime')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Process voice message with comprehensive error handling"""
    
    try:
        # Parse and validate input
        body = json.loads(event.get('body', '{}'))
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        
        if not user_id:
            return create_response(400, {'error': 'User not authenticated'})
        
        # Validate required fields
        required_fields = ['message', 'type', 'session_id']
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return create_response(400, {
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            })
        
        # Process message based on type
        if body['type'] == 'voice':
            return process_voice_message(body, user_id)
        elif body['type'] == 'text':
            return process_text_message(body, user_id)
        else:
            return create_response(400, {'error': 'Invalid message type'})
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return create_response(400, {'error': 'Invalid JSON format'})
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def process_voice_message(body: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Process voice message with error handling"""
    try:
        # Upload audio to S3
        audio_key = f"audio/{user_id}/{body['session_id']}/{context.aws_request_id}.wav"
        
        s3_client.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key=audio_key,
            Body=base64.b64decode(body.get('audio_data', '')),
            ContentType='audio/wav'
        )
        
        # Process with Lex
        lex_response = lex_client.recognize_text(
            botId=os.environ['LEX_BOT_ID'],
            botAliasId='TSTALIASID',
            localeId='en_US',
            sessionId=body['session_id'],
            text=body.get('transcription', body['message'])
        )
        
        # Store conversation
        store_conversation(user_id, body, lex_response, audio_key)
        
        return create_response(200, {
            'response': lex_response['messages'][0]['content'],
            'intent': lex_response.get('interpretations', [{}])[0].get('intent', {}).get('name'),
            'session_id': body['session_id']
        })
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            logger.error(f"S3 bucket not found: {os.environ['S3_BUCKET']}")
            return create_response(500, {'error': 'Storage service unavailable'})
        elif error_code == 'AccessDenied':
            logger.error("Access denied to S3 bucket")
            return create_response(500, {'error': 'Storage access denied'})
        else:
            logger.error(f"AWS service error: {e}")
            return create_response(500, {'error': 'Service temporarily unavailable'})
    
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        return create_response(500, {'error': 'Voice processing failed'})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }
```

### Question 2: DynamoDB Query Optimization
**Scenario**: Implement efficient DynamoDB queries for conversation history.

```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class ConversationService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('voice-assistant-conversations')
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's recent conversations efficiently
        
        Requirements:
        - Return most recent conversations first
        - Implement pagination
        - Handle errors gracefully
        - Optimize for performance
        """
        # Your implementation here
        pass
    
    def get_conversation_by_session(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a specific conversation session"""
        # Your implementation here
        pass
    
    def search_conversations_by_intent(self, user_id: str, intent_name: str, 
                                     days_back: int = 30) -> List[Dict[str, Any]]:
        """Search conversations by intent within time range"""
        # Your implementation here
        pass
```

**Expected Solution**:
```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('voice-assistant-conversations')
    
    def get_user_conversations(self, user_id: str, limit: int = 50, 
                             last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """Get user's recent conversations with pagination"""
        try:
            query_params = {
                'KeyConditionExpression': Key('user_id').eq(user_id),
                'ScanIndexForward': False,  # Most recent first
                'Limit': limit
            }
            
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.query(**query_params)
            
            return {
                'conversations': response['Items'],
                'last_evaluated_key': response.get('LastEvaluatedKey'),
                'count': response['Count']
            }
            
        except Exception as e:
            logger.error(f"Error querying conversations: {str(e)}")
            raise
    
    def get_conversation_by_session(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a specific conversation session"""
        try:
            response = self.table.query(
                IndexName='session-index',
                KeyConditionExpression=Key('session_id').eq(session_id),
                FilterExpression=Attr('user_id').eq(user_id),
                ScanIndexForward=True  # Chronological order
            )
            
            return response['Items']
            
        except Exception as e:
            logger.error(f"Error querying session conversations: {str(e)}")
            raise
    
    def search_conversations_by_intent(self, user_id: str, intent_name: str, 
                                     days_back: int = 30) -> List[Dict[str, Any]]:
        """Search conversations by intent within time range"""
        try:
            # Calculate timestamp for time range
            cutoff_time = int((datetime.utcnow() - timedelta(days=days_back)).timestamp())
            
            response = self.table.query(
                IndexName='timestamp-index',
                KeyConditionExpression=Key('user_id').eq(user_id) & Key('timestamp').gte(cutoff_time),
                FilterExpression=Attr('intent_name').eq(intent_name),
                ScanIndexForward=False
            )
            
            return response['Items']
            
        except Exception as e:
            logger.error(f"Error searching conversations by intent: {str(e)}")
            raise
    
    def batch_get_conversations(self, conversation_ids: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Efficiently retrieve multiple conversations"""
        try:
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    self.table.table_name: {
                        'Keys': conversation_ids
                    }
                }
            )
            
            return response['Responses'][self.table.table_name]
            
        except Exception as e:
            logger.error(f"Error batch getting conversations: {str(e)}")
            raise
```

### Question 3: Async Processing with SQS
**Scenario**: Implement asynchronous voice processing using SQS.

```python
import asyncio
import boto3
import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class AsyncVoiceProcessor:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/voice-processing-queue'
    
    async def process_voice_batch(self, voice_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple voice messages asynchronously
        
        Requirements:
        - Send messages to SQS for processing
        - Handle batch operations efficiently
        - Implement proper error handling
        - Return processing status for each message
        """
        # Your implementation here
        pass
    
    def send_to_queue(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send single message to SQS queue"""
        # Your implementation here
        pass
    
    async def poll_queue_and_process(self, max_messages: int = 10) -> None:
        """Poll SQS queue and process messages"""
        # Your implementation here
        pass
```

**Expected Solution**:
```python
import asyncio
import boto3
import json
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AsyncVoiceProcessor:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/voice-processing-queue'
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def process_voice_batch(self, voice_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple voice messages asynchronously"""
        tasks = []
        
        for message in voice_messages:
            task = asyncio.create_task(self._process_single_message(message))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'message_id': voice_messages[i].get('id'),
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process single voice message asynchronously"""
        loop = asyncio.get_event_loop()
        
        try:
            # Send to queue asynchronously
            result = await loop.run_in_executor(
                self.executor, 
                self.send_to_queue, 
                message
            )
            
            return {
                'message_id': message.get('id'),
                'status': 'queued',
                'sqs_message_id': result.get('MessageId')
            }
            
        except Exception as e:
            logger.error(f"Error processing message {message.get('id')}: {str(e)}")
            raise
    
    def send_to_queue(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send single message to SQS queue"""
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'voice_processing',
                        'DataType': 'String'
                    },
                    'Priority': {
                        'StringValue': message.get('priority', 'normal'),
                        'DataType': 'String'
                    }
                }
            )
            
            return response
            
        except ClientError as e:
            logger.error(f"Error sending message to SQS: {e}")
            raise
    
    async def poll_queue_and_process(self, max_messages: int = 10) -> None:
        """Poll SQS queue and process messages"""
        while True:
            try:
                # Poll messages from queue
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=max_messages,
                    WaitTimeSeconds=20,  # Long polling
                    MessageAttributeNames=['All']
                )
                
                messages = response.get('Messages', [])
                
                if messages:
                    # Process messages concurrently
                    tasks = [
                        self._process_queue_message(msg) 
                        for msg in messages
                    ]
                    
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Small delay before next poll
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error polling queue: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_queue_message(self, sqs_message: Dict[str, Any]) -> None:
        """Process individual message from queue"""
        try:
            # Parse message body
            message_body = json.loads(sqs_message['Body'])
            
            # Process the voice message
            # (Implementation would depend on specific processing logic)
            await self._handle_voice_processing(message_body)
            
            # Delete message from queue after successful processing
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=sqs_message['ReceiptHandle']
            )
            
            logger.info(f"Successfully processed message: {sqs_message['MessageId']}")
            
        except Exception as e:
            logger.error(f"Error processing queue message: {str(e)}")
            # Message will be returned to queue for retry
    
    async def _handle_voice_processing(self, message: Dict[str, Any]) -> None:
        """Handle the actual voice processing logic"""
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Implementation would include:
        # - Audio transcription
        # - Lex processing
        # - Database storage
        # - Response generation
        pass
```

## ⚛️ React/TypeScript Coding Questions

### Question 4: Voice Recording Hook
**Scenario**: Create a custom React hook for voice recording functionality.

```typescript
import { useState, useRef, useCallback } from 'react';

interface UseVoiceRecordingReturn {
  isRecording: boolean;
  audioBlob: Blob | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  clearRecording: () => void;
  error: string | null;
}

export const useVoiceRecording = (): UseVoiceRecordingReturn => {
  // Your implementation here
  // Requirements:
  // - Handle browser compatibility
  // - Manage recording state
  // - Handle errors gracefully
  // - Return audio blob for upload
  // - Support recording controls
};
```

**Expected Solution**:
```typescript
import { useState, useRef, useCallback, useEffect } from 'react';

interface UseVoiceRecordingReturn {
  isRecording: boolean;
  audioBlob: Blob | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  clearRecording: () => void;
  error: string | null;
  duration: number;
}

export const useVoiceRecording = (): UseVoiceRecordingReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = useCallback(async (): Promise<void> => {
    try {
      setError(null);
      
      // Check browser support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Voice recording is not supported in this browser');
      }

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });

      streamRef.current = stream;
      audioChunksRef.current = [];

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm' 
        });
        setAudioBlob(audioBlob);
        
        // Clean up stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setDuration(0);

      // Start duration timer
      intervalRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
      setError(errorMessage);
      console.error('Recording error:', err);
    }
  }, []);

  const stopRecording = useCallback((): void => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [isRecording]);

  const clearRecording = useCallback((): void => {
    setAudioBlob(null);
    setError(null);
    setDuration(0);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    isRecording,
    audioBlob,
    startRecording,
    stopRecording,
    clearRecording,
    error,
    duration
  };
};
```

### Question 5: Chat Message Component
**Scenario**: Create a reusable chat message component with TypeScript.

```typescript
import React from 'react';
import styled from 'styled-components';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  messageType: 'text' | 'voice';
  audioUrl?: string;
  isLoading?: boolean;
}

interface ChatMessageProps {
  message: Message;
  onAudioPlay?: (audioUrl: string) => void;
  onRetry?: (messageId: string) => void;
  className?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onAudioPlay,
  onRetry,
  className
}) => {
  // Your implementation here
  // Requirements:
  // - Display different styles for user vs bot messages
  // - Handle voice message playback
  // - Show loading states
  // - Format timestamps
  // - Handle retry functionality
  // - Responsive design
};
```

**Expected Solution**:
```typescript
import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { FaPlay, FaPause, FaRedo, FaUser, FaRobot } from 'react-icons/fa';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  messageType: 'text' | 'voice';
  audioUrl?: string;
  isLoading?: boolean;
  error?: string;
}

interface ChatMessageProps {
  message: Message;
  onAudioPlay?: (audioUrl: string) => void;
  onRetry?: (messageId: string) => void;
  className?: string;
}

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const Avatar = styled.div<{ isUser: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.isUser ? '#007bff' : '#28a745'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: ${props => props.isUser ? '0 0 0 0.5rem' : '0 0.5rem 0 0'};
  font-size: 1.2rem;
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 70%;
  background: ${props => props.isUser ? '#007bff' : '#f8f9fa'};
  color: ${props => props.isUser ? 'white' : '#333'};
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  &::before {
    content: '';
    position: absolute;
    top: 10px;
    ${props => props.isUser ? 'right: -8px' : 'left: -8px'};
    width: 0;
    height: 0;
    border-style: solid;
    border-width: ${props => props.isUser ? '8px 0 8px 8px' : '8px 8px 8px 0'};
    border-color: ${props => props.isUser 
      ? `transparent transparent transparent #007bff` 
      : `transparent #f8f9fa transparent transparent`};
  }

  @media (max-width: 768px) {
    max-width: 85%;
  }
`;

const MessageContent = styled.div`
  margin-bottom: 0.5rem;
  line-height: 1.4;
  word-wrap: break-word;
`;

const MessageMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.5rem;
`;

const AudioControls = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
`;

const AudioButton = styled.button`
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const LoadingDots = styled.div`
  display: inline-flex;
  gap: 2px;
  
  span {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: currentColor;
    animation: loading 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }
  
  @keyframes loading {
    0%, 80%, 100% { opacity: 0.3; }
    40% { opacity: 1; }
  }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const RetryButton = styled.button`
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 0.25rem;
  
  &:hover {
    color: #c82333;
  }
`;

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onAudioPlay,
  onRetry,
  className
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const formatTimestamp = (timestamp: Date): string => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const handleAudioPlay = async () => {
    if (!message.audioUrl) return;

    if (isPlaying) {
      audioRef.current?.pause();
      setIsPlaying(false);
    } else {
      try {
        if (!audioRef.current) {
          audioRef.current = new Audio(message.audioUrl);
          audioRef.current.onended = () => setIsPlaying(false);
        }
        
        await audioRef.current.play();
        setIsPlaying(true);
        onAudioPlay?.(message.audioUrl);
      } catch (error) {
        console.error('Audio playback failed:', error);
      }
    }
  };

  const handleRetry = () => {
    onRetry?.(message.id);
  };

  return (
    <MessageContainer isUser={message.type === 'user'} className={className}>
      {message.type === 'bot' && (
        <Avatar isUser={false}>
          <FaRobot />
        </Avatar>
      )}
      
      <MessageBubble isUser={message.type === 'user'}>
        <MessageContent>
          {message.isLoading ? (
            <LoadingDots>
              <span />
              <span />
              <span />
            </LoadingDots>
          ) : (
            message.content
          )}
        </MessageContent>

        {message.messageType === 'voice' && message.audioUrl && (
          <AudioControls>
            <AudioButton onClick={handleAudioPlay}>
              {isPlaying ? <FaPause /> : <FaPlay />}
            </AudioButton>
            <span>🎤</span>
          </AudioControls>
        )}

        {message.error && (
          <ErrorMessage>
            <span>Failed to send</span>
            <RetryButton onClick={handleRetry}>
              <FaRedo />
            </RetryButton>
          </ErrorMessage>
        )}

        <MessageMeta>
          <span>{formatTimestamp(message.timestamp)}</span>
          {message.messageType === 'voice' && <span>🎤</span>}
        </MessageMeta>
      </MessageBubble>

      {message.type === 'user' && (
        <Avatar isUser={true}>
          <FaUser />
        </Avatar>
      )}
    </MessageContainer>
  );
};
```

## 🔧 Infrastructure/DevOps Coding Questions

### Question 6: Terraform Module for Lambda
**Scenario**: Create a reusable Terraform module for Lambda functions.

```hcl
# modules/lambda/variables.tf
variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "runtime" {
  description = "Runtime for the Lambda function"
  type        = string
  default     = "python3.9"
}

variable "handler" {
  description = "Function handler"
  type        = string
  default     = "handler.lambda_handler"
}

variable "source_code_path" {
  description = "Path to the source code"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for the function"
  type        = map(string)
  default     = {}
}

variable "timeout" {
  description = "Function timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size in MB"
  type        = number
  default     = 512
}

# Your implementation for main.tf
# Requirements:
# - Create Lambda function with proper IAM role
# - Support environment variables
# - Enable CloudWatch logging
# - Support VPC configuration (optional)
# - Create CloudWatch log group
# - Support tags
```

**Expected Solution**:
```hcl
# modules/lambda/main.tf
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Create ZIP file for Lambda deployment
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_code_path
  output_path = "${path.module}/lambda_${var.function_name}.zip"
}

# IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# VPC execution policy (if VPC is configured)
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  count      = var.vpc_config != null ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# CloudWatch log group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = var.tags
}

# Lambda function
resource "aws_lambda_function" "function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = var.handler
  runtime         = var.runtime
  timeout         = var.timeout
  memory_size     = var.memory_size
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = merge(
      var.environment_variables,
      {
        LOG_LEVEL = var.log_level
      }
    )
  }

  dynamic "vpc_config" {
    for_each = var.vpc_config != null ? [var.vpc_config] : []
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }

  dynamic "dead_letter_config" {
    for_each = var.dead_letter_target_arn != null ? [1] : []
    content {
      target_arn = var.dead_letter_target_arn
    }
  }

  tracing_config {
    mode = var.enable_tracing ? "Active" : "PassThrough"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = var.tags
}

# Lambda alias
resource "aws_lambda_alias" "alias" {
  count            = var.create_alias ? 1 : 0
  name             = var.alias_name
  description      = "Alias for ${var.function_name}"
  function_name    = aws_lambda_function.function.function_name
  function_version = aws_lambda_function.function.version
}

# CloudWatch metric alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.function_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.error_threshold
  alarm_description   = "This metric monitors lambda errors"
  alarm_actions       = var.alarm_actions

  dimensions = {
    FunctionName = aws_lambda_function.function.function_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.function_name}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = var.duration_threshold
  alarm_description   = "This metric monitors lambda duration"
  alarm_actions       = var.alarm_actions

  dimensions = {
    FunctionName = aws_lambda_function.function.function_name
  }

  tags = var.tags
}
```

These coding questions test practical implementation skills that would be directly applicable to the Voice Assistant AI project. They cover error handling, async programming, React hooks, TypeScript, and infrastructure as code - all key technologies used in the project.

**Tips for Answering Coding Questions:**
1. **Start with clarifying questions** about requirements
2. **Think out loud** about your approach
3. **Handle edge cases** and error scenarios
4. **Write clean, readable code** with proper naming
5. **Consider performance** and scalability
6. **Add comments** to explain complex logic
7. **Test your solution** mentally or with examples
