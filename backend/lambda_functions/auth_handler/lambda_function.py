import json
import boto3
import os
import logging
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp')

# Environment variables
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'voice-assistant-ai-prod-conversations')
USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID', 'us-east-1_ID7e0JI2c')

def lambda_handler(event, context):
    """
    Main Lambda handler for authentication functionality
    """
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle CORS preflight requests
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
        
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', '')
        
        logger.info(f"Processing auth action: {action}")
        
        # Route to appropriate handler
        if action == 'validate_token':
            return validate_token(body)
        elif action == 'get_user_profile':
            return get_user_profile(body)
        elif action == 'update_user_profile':
            return update_user_profile(body)
        elif action == 'health_check':
            return health_check()
        else:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Invalid action',
                    'message': 'Please specify a valid action',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
    except Exception as e:
        logger.error(f"Error processing auth request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Sorry, something went wrong with authentication.',
                'timestamp': datetime.now().isoformat()
            })
        }

def validate_token(body):
    """
    Validate JWT token
    """
    try:
        access_token = body.get('access_token', '')
        
        if not access_token:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Missing token',
                    'message': 'Access token is required',
                    'valid': False
                })
            }
        
        # Validate token with Cognito
        try:
            response = cognito_client.get_user(AccessToken=access_token)
            
            user_attributes = {}
            for attr in response.get('UserAttributes', []):
                user_attributes[attr['Name']] = attr['Value']
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'valid': True,
                    'user': {
                        'username': response.get('Username'),
                        'email': user_attributes.get('email'),
                        'email_verified': user_attributes.get('email_verified') == 'true',
                        'sub': user_attributes.get('sub')
                    },
                    'timestamp': datetime.now().isoformat()
                })
            }
            
        except cognito_client.exceptions.NotAuthorizedException:
            return {
                'statusCode': 401,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'valid': False,
                    'error': 'Invalid token',
                    'message': 'The provided token is invalid or expired'
                })
            }
            
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'valid': False,
                'error': 'Validation failed',
                'message': 'Unable to validate token'
            })
        }

def get_user_profile(body):
    """
    Get user profile information
    """
    try:
        user_id = body.get('user_id', '')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Missing user ID',
                    'message': 'User ID is required'
                })
            }
        
        # Get user profile from DynamoDB (if stored) or return basic info
        profile = {
            'user_id': user_id,
            'preferences': {
                'voice_enabled': True,
                'notifications': True,
                'theme': 'light'
            },
            'stats': {
                'conversations': 0,
                'last_active': datetime.now().isoformat()
            }
        }
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'profile': profile,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Profile retrieval failed',
                'message': 'Unable to retrieve user profile'
            })
        }

def update_user_profile(body):
    """
    Update user profile information
    """
    try:
        user_id = body.get('user_id', '')
        preferences = body.get('preferences', {})
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Missing user ID',
                    'message': 'User ID is required'
                })
            }
        
        # Here you would typically update the user profile in DynamoDB
        # For now, we'll just return success
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Profile updated successfully',
                'user_id': user_id,
                'preferences': preferences,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Profile update failed',
                'message': 'Unable to update user profile'
            })
        }

def health_check():
    """
    Health check endpoint
    """
    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'status': 'healthy',
            'service': 'auth-handler',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    }

def get_cors_headers():
    """
    Get CORS headers
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
