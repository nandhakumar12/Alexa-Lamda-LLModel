"""
Voice Assistant AI - Authentication Handler Lambda Function
Handles user authentication, JWT tokens, and Cognito integration
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

import boto3
import jwt
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
except ImportError:
    # Fallback for local development
    pass

# Initialize AWS Lambda Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Initialize AWS clients
cognito_client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
JWT_SECRET = os.environ.get('JWT_SECRET', 'default-secret-change-in-production')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

# Constants
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


class AuthenticationHandler:
    """Main authentication class for handling user auth operations"""
    
    def __init__(self):
        self.cognito_client = cognito_client
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    @tracer.capture_method
    def register_user(self, email: str, password: str, user_attributes: Dict[str, str] = None) -> Dict[str, Any]:
        """Register a new user with Cognito"""
        try:
            # Prepare user attributes
            attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ]
            
            if user_attributes:
                for key, value in user_attributes.items():
                    attributes.append({'Name': key, 'Value': value})
            
            # Create user in Cognito
            response = self.cognito_client.admin_create_user(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=email,
                UserAttributes=attributes,
                TemporaryPassword=password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Set permanent password
            self.cognito_client.admin_set_user_password(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=email,
                Password=password,
                Permanent=True
            )
            
            user_id = response['User']['Username']
            
            # Store user session in DynamoDB
            session_data = {
                'session_id': str(uuid.uuid4()),
                'user_id': user_id,
                'email': email,
                'created_at': int(datetime.now(timezone.utc).timestamp()),
                'last_activity': int(datetime.now(timezone.utc).timestamp()),
                'status': 'active',
                'environment': ENVIRONMENT
            }
            
            self.table.put_item(Item=session_data)
            
            # Generate JWT token
            token = self._generate_jwt_token(user_id, email)
            
            # Emit custom metrics
            metrics.add_metric(name="UserRegistered", unit=MetricUnit.Count, value=1)
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email,
                'token': token,
                'session_id': session_data['session_id']
            }
            
        except self.cognito_client.exceptions.UsernameExistsException:
            logger.warning(f"User registration failed: email already exists - {email}")
            metrics.add_metric(name="UserRegistrationFailed", unit=MetricUnit.Count, value=1)
            return {
                'success': False,
                'error': 'User already exists',
                'error_code': 'USER_EXISTS'
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            metrics.add_metric(name="UserRegistrationError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Cognito"""
        try:
            # Authenticate with Cognito
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=COGNITO_USER_POOL_ID,
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # Extract tokens
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']
            
            # Get user information
            user_info = self.cognito_client.get_user(AccessToken=access_token)
            user_id = user_info['Username']
            
            # Update user session in DynamoDB
            session_data = {
                'session_id': str(uuid.uuid4()),
                'user_id': user_id,
                'email': email,
                'last_activity': int(datetime.now(timezone.utc).timestamp()),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'status': 'active',
                'environment': ENVIRONMENT,
                'expires_at': int((datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp())
            }
            
            self.table.put_item(Item=session_data)
            
            # Generate custom JWT token
            token = self._generate_jwt_token(user_id, email)
            
            # Emit custom metrics
            metrics.add_metric(name="UserAuthenticated", unit=MetricUnit.Count, value=1)
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email,
                'token': token,
                'session_id': session_data['session_id'],
                'cognito_tokens': {
                    'access_token': access_token,
                    'id_token': id_token,
                    'refresh_token': refresh_token
                }
            }
            
        except self.cognito_client.exceptions.NotAuthorizedException:
            logger.warning(f"Authentication failed for user: {email}")
            metrics.add_metric(name="AuthenticationFailed", unit=MetricUnit.Count, value=1)
            return {
                'success': False,
                'error': 'Invalid credentials',
                'error_code': 'INVALID_CREDENTIALS'
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            metrics.add_metric(name="AuthenticationError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh user authentication token"""
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            # Extract new tokens
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            
            # Get user information
            user_info = self.cognito_client.get_user(AccessToken=access_token)
            user_id = user_info['Username']
            email = next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'email'), '')
            
            # Generate new JWT token
            token = self._generate_jwt_token(user_id, email)
            
            # Emit custom metrics
            metrics.add_metric(name="TokenRefreshed", unit=MetricUnit.Count, value=1)
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email,
                'token': token,
                'cognito_tokens': {
                    'access_token': access_token,
                    'id_token': id_token
                }
            }
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            metrics.add_metric(name="TokenRefreshError", unit=MetricUnit.Count, value=1)
            return {
                'success': False,
                'error': 'Invalid refresh token',
                'error_code': 'INVALID_REFRESH_TOKEN'
            }
    
    @tracer.capture_method
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            user_id = payload.get('user_id')
            email = payload.get('email')
            exp = payload.get('exp')
            
            # Check if token is expired
            if datetime.now(timezone.utc).timestamp() > exp:
                return {
                    'valid': False,
                    'error': 'Token expired',
                    'error_code': 'TOKEN_EXPIRED'
                }
            
            # Emit custom metrics
            metrics.add_metric(name="TokenValidated", unit=MetricUnit.Count, value=1)
            
            return {
                'valid': True,
                'user_id': user_id,
                'email': email
            }
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            metrics.add_metric(name="TokenValidationFailed", unit=MetricUnit.Count, value=1)
            return {
                'valid': False,
                'error': 'Invalid token',
                'error_code': 'INVALID_TOKEN'
            }
    
    @tracer.capture_method
    def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            # Update session status in DynamoDB
            self.table.update_item(
                Key={'session_id': session_id},
                UpdateExpression='SET #status = :status, last_activity = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'inactive',
                    ':timestamp': int(datetime.now(timezone.utc).timestamp())
                }
            )
            
            # Emit custom metrics
            metrics.add_metric(name="UserLoggedOut", unit=MetricUnit.Count, value=1)
            
            return {
                'success': True,
                'message': 'User logged out successfully'
            }
            
        except Exception as e:
            logger.error(f"Error logging out user: {str(e)}")
            metrics.add_metric(name="LogoutError", unit=MetricUnit.Count, value=1)
            raise
    
    def _generate_jwt_token(self, user_id: str, email: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'iat': datetime.now(timezone.utc).timestamp(),
            'exp': (datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Main Lambda handler for authentication functionality"""
    
    try:
        logger.info("Processing authentication request", extra={"event": event})
        
        # Initialize auth handler
        auth_handler = AuthenticationHandler()
        
        # Parse request
        if 'httpMethod' in event:
            # API Gateway request
            http_method = event['httpMethod']
            body = json.loads(event.get('body', '{}'))
            action = body.get('action')
            
            if http_method == 'POST':
                if action == 'register':
                    email = body.get('email')
                    password = body.get('password')
                    user_attributes = body.get('user_attributes', {})
                    
                    if not email or not password:
                        return {
                            'statusCode': 400,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({'error': 'Email and password are required'})
                        }
                    
                    response = auth_handler.register_user(email, password, user_attributes)
                    
                elif action == 'login':
                    email = body.get('email')
                    password = body.get('password')
                    
                    if not email or not password:
                        return {
                            'statusCode': 400,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({'error': 'Email and password are required'})
                        }
                    
                    response = auth_handler.authenticate_user(email, password)
                    
                elif action == 'refresh':
                    refresh_token = body.get('refresh_token')
                    
                    if not refresh_token:
                        return {
                            'statusCode': 400,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({'error': 'Refresh token is required'})
                        }
                    
                    response = auth_handler.refresh_token(refresh_token)
                    
                elif action == 'validate':
                    token = body.get('token')
                    
                    if not token:
                        return {
                            'statusCode': 400,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({'error': 'Token is required'})
                        }
                    
                    response = auth_handler.validate_token(token)
                    
                elif action == 'logout':
                    session_id = body.get('session_id')
                    
                    if not session_id:
                        return {
                            'statusCode': 400,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({'error': 'Session ID is required'})
                        }
                    
                    response = auth_handler.logout_user(session_id)
                    
                else:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Invalid action'})
                    }
                
                status_code = 200 if response.get('success', response.get('valid', False)) else 400
                
                return {
                    'statusCode': status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(response)
                }
            
            else:
                return {
                    'statusCode': 405,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Method not allowed'})
                }
        
        else:
            # Direct Lambda invocation
            logger.info("Direct Lambda invocation")
            return {'statusCode': 200, 'body': 'Auth handler is running'}
    
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
