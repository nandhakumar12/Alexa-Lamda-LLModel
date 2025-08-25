import json
import boto3
import os
from datetime import datetime
import uuid

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Model configuration for cost optimization - Claude Haiku is cheapest
MODEL_CONFIG = {
    'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',  # Most cost-effective
    'max_tokens': 300,  # Reduced for cost savings
    'temperature': 0.7
}

# DynamoDB table for conversation history
CONVERSATION_TABLE = os.environ.get('CONVERSATION_TABLE', 'voice-assistant-conversations')

def lambda_handler(event, context):
    """
    Advanced LLM-powered chatbot handler using AWS Bedrock Claude Haiku
    """
    try:
        # Parse the incoming request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        user_message = body.get('message', '')
        user_id = body.get('user_id', 'nandhakumar')
        conversation_id = body.get('conversation_id', str(uuid.uuid4()))

        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'error': 'Message is required'})
            }

        # Get conversation history
        conversation_history = get_conversation_history(user_id, conversation_id)

        # Generate LLM response using Bedrock
        llm_response = generate_llm_response(user_message, conversation_history, user_id)

        # Save conversation to DynamoDB
        save_conversation(user_id, conversation_id, user_message, llm_response)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'message': llm_response,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'model': MODEL_CONFIG['model_id']
            })
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'I apologize, but I encountered a technical issue. Please try again.'
            })
        }

def get_conversation_history(user_id, conversation_id, limit=6):
    """
    Retrieve conversation history from DynamoDB (limited for cost optimization)
    """
    try:
        table = dynamodb.Table(CONVERSATION_TABLE)

        response = table.query(
            KeyConditionExpression='user_id = :user_id AND begins_with(sort_key, :conv_id)',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':conv_id': f"{conversation_id}#"
            },
            ScanIndexForward=False,  # Get most recent first
            Limit=limit * 2  # Get both user and assistant messages
        )

        # Format conversation history for Claude
        messages = []
        for item in reversed(response['Items']):  # Reverse to get chronological order
            if item['message_type'] == 'user':
                messages.append({"role": "user", "content": item['message']})
            elif item['message_type'] == 'assistant':
                messages.append({"role": "assistant", "content": item['message']})

        return messages[-limit:] if len(messages) > limit else messages

    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

def generate_llm_response(user_message, conversation_history, user_id):
    """
    Generate response using AWS Bedrock Claude Haiku (most cost-effective)
    Cost: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens
    """
    try:
        # Build conversation context (optimized for cost)
        context = ""
        if conversation_history:
            # Only include last 4 exchanges to minimize tokens
            recent_history = conversation_history[-8:]  # 4 user + 4 assistant messages
            for msg in recent_history:
                role = "Human" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"

        # Optimized system prompt for Claude Haiku
        system_prompt = f"""You are Nandhakumar's AI assistant. Be helpful, conversational, and concise.

Capabilities:
- Music control (Nandhakumar's favorites: Space Ambient, Cosmic Journey, Stellar Dreams, Galactic Waves, Interstellar Theme, Future Bass, Chill Vibes, Synthwave Night)
- Weather, time, smart home, general knowledge, programming help

For music commands, respond with:
- MUSIC_PLAY:[song_name] - to play specific song
- MUSIC_RANDOM - for random song
- MUSIC_STOP - to stop
- MUSIC_LIST - to list songs

Keep responses friendly and under 150 words. User: {user_id}"""

        # Prepare prompt for Claude (Anthropic format)
        full_prompt = f"""Human: {system_prompt}

{context}
Human: {user_message}
Assistant:"""

        # Prepare request body for Bedrock Claude Haiku
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MODEL_CONFIG['max_tokens'],
            "temperature": MODEL_CONFIG['temperature'],
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }

        # Call AWS Bedrock
        response = bedrock.invoke_model(
            modelId=MODEL_CONFIG['model_id'],
            body=json.dumps(request_body),
            contentType='application/json'
        )

        # Parse response
        response_body = json.loads(response['body'].read())
        assistant_response = response_body['content'][0]['text']

        return assistant_response.strip()

    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

def save_conversation(user_id, conversation_id, user_message, assistant_response):
    """
    Save conversation to DynamoDB
    """
    try:
        table = dynamodb.Table(CONVERSATION_TABLE)
        timestamp = datetime.now().isoformat()

        # Save user message
        table.put_item(
            Item={
                'user_id': user_id,
                'sort_key': f"{conversation_id}#{timestamp}#user",
                'conversation_id': conversation_id,
                'message': user_message,
                'message_type': 'user',
                'timestamp': timestamp
            }
        )

        # Save assistant response
        table.put_item(
            Item={
                'user_id': user_id,
                'sort_key': f"{conversation_id}#{timestamp}#assistant",
                'conversation_id': conversation_id,
                'message': assistant_response,
                'message_type': 'assistant',
                'timestamp': timestamp
            }
        )

    except Exception as e:
        print(f"Error saving conversation: {e}")
