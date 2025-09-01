import json
import boto3
import os
from datetime import datetime

# Initialize Lambda client
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Proxy function to invoke the LLM chatbot Lambda function
    This provides a simple HTTP endpoint that can be called from the frontend
    """
    try:
        # Parse the incoming request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        user_message = body.get('message', '')
        user_id = body.get('user_id', 'anonymous')
        
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
        
        # Prepare payload for the LLM Lambda function
        llm_payload = {
            'body': json.dumps({
                'message': user_message,
                'user_id': user_id
            })
        }
        
        # Invoke the LLM Lambda function
        response = lambda_client.invoke(
            FunctionName='voice-assistant-llm-chatbot',
            InvocationType='RequestResponse',
            Payload=json.dumps(llm_payload)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        
        if response_payload.get('statusCode') == 200:
            # Extract the response body
            response_body = json.loads(response_payload['body'])
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({
                    'message': response_body.get('message', 'Response received'),
                    'conversation_id': response_body.get('conversation_id'),
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id,
                    'source': 'llm-proxy'
                })
            }
        else:
            # LLM function returned an error
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({
                    'error': 'LLM service error',
                    'message': 'I apologize, but I encountered a technical issue. Please try again.'
                })
            }
        
    except Exception as e:
        print(f"Error in llm_proxy: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': 'Proxy error',
                'message': 'I apologize, but I encountered a technical issue. Please try again.'
            })
        }
