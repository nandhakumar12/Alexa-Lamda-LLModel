"""
AWS Secrets Manager Helper Functions
Provides secure access to secrets stored in AWS Secrets Manager
"""

import json
import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger(__name__)

class SecretsManager:
    """
    AWS Secrets Manager client for retrieving and managing secrets
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize Secrets Manager client
        
        Args:
            region_name (str): AWS region name
        """
        self.region_name = region_name
        self.client = boto3.client('secretsmanager', region_name=region_name)
        
    def get_secret(self, secret_name: str, version_stage: str = 'AWSCURRENT') -> Optional[Dict[str, Any]]:
        """
        Retrieve a secret from AWS Secrets Manager
        
        Args:
            secret_name (str): Name or ARN of the secret
            version_stage (str): Version stage (default: AWSCURRENT)
            
        Returns:
            Dict containing the secret data, or None if error
        """
        try:
            response = self.client.get_secret_value(
                SecretId=secret_name,
                VersionStage=version_stage
            )
            
            # Parse JSON secret string
            secret_data = json.loads(response['SecretString'])
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret {secret_name} not found")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret {secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret {secret_name}")
            elif error_code == 'DecryptionFailureException':
                logger.error(f"Decryption failed for secret {secret_name}")
            elif error_code == 'InternalServiceErrorException':
                logger.error(f"Internal service error for secret {secret_name}")
            else:
                logger.error(f"Error retrieving secret {secret_name}: {e}")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from secret {secret_name}: {e}")
            return None
            
        except BotoCoreError as e:
            logger.error(f"Boto3 error retrieving secret {secret_name}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret {secret_name}: {e}")
            return None
    
    def get_jwt_secret(self) -> Optional[str]:
        """
        Get JWT signing secret
        
        Returns:
            JWT secret string or None
        """
        secret_data = self.get_secret('voice-assistant-ai/jwt-secret')
        if secret_data:
            # For JWT secret, the entire secret string is the secret
            return secret_data
        return None
    
    def get_api_keys(self) -> Optional[Dict[str, str]]:
        """
        Get API keys and external service credentials
        
        Returns:
            Dictionary of API keys or None
        """
        return self.get_secret('voice-assistant-ai/api-keys')
    
    def get_database_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get database credentials
        
        Returns:
            Dictionary of database credentials or None
        """
        return self.get_secret('voice-assistant-ai/database')
    
    def get_app_config(self) -> Optional[Dict[str, Any]]:
        """
        Get application configuration
        
        Returns:
            Dictionary of app configuration or None
        """
        return self.get_secret('voice-assistant-ai/app-config')
    
    def get_external_services(self) -> Optional[Dict[str, str]]:
        """
        Get external service credentials
        
        Returns:
            Dictionary of external service credentials or None
        """
        return self.get_secret('voice-assistant-ai/external-services')
    
    def update_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """
        Update a secret value
        
        Args:
            secret_name (str): Name or ARN of the secret
            secret_value (Dict): New secret value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Successfully updated secret: {secret_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error updating secret {secret_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating secret {secret_name}: {e}")
            return False

# Global instance for easy import
secrets_manager = SecretsManager()

# Convenience functions for common secrets
def get_jwt_secret() -> Optional[str]:
    """Get JWT secret"""
    return secrets_manager.get_jwt_secret()

def get_claude_api_key() -> Optional[str]:
    """Get Claude API key"""
    api_keys = secrets_manager.get_api_keys()
    if api_keys:
        return api_keys.get('claude_api_key')
    return None

def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key"""
    api_keys = secrets_manager.get_api_keys()
    if api_keys:
        return api_keys.get('openai_api_key')
    return None

def get_encryption_key() -> Optional[str]:
    """Get encryption key"""
    api_keys = secrets_manager.get_api_keys()
    if api_keys:
        return api_keys.get('encryption_key')
    return None

def get_database_password() -> Optional[str]:
    """Get database password"""
    db_creds = secrets_manager.get_database_credentials()
    if db_creds:
        return db_creds.get('password')
    return None

def get_app_config_value(key: str, default: Any = None) -> Any:
    """Get specific app configuration value"""
    app_config = secrets_manager.get_app_config()
    if app_config:
        return app_config.get(key, default)
    return default

# Example usage and testing
if __name__ == "__main__":
    # Test the secrets manager
    print("Testing AWS Secrets Manager...")
    
    # Test JWT secret
    jwt_secret = get_jwt_secret()
    print(f"JWT Secret: {'Found' if jwt_secret else 'Not found'}")
    
    # Test API keys
    claude_key = get_claude_api_key()
    print(f"Claude API Key: {'Found' if claude_key else 'Not found'}")
    
    # Test app config
    max_tokens = get_app_config_value('max_tokens', 1000)
    print(f"Max Tokens: {max_tokens}")

