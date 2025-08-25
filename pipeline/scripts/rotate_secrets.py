#!/usr/bin/env python3
"""
Automated Secrets Rotation Script
Rotates secrets in AWS Secrets Manager for Voice Assistant AI
"""

import json
import argparse
import boto3
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecretsRotator:
    """Handles automated rotation of secrets in AWS Secrets Manager"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.secrets_client = boto3.client('secretsmanager', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.ssm_client = boto3.client('ssm', region_name=region)
        
    def list_secrets_for_rotation(self, project_name: str) -> List[Dict[str, Any]]:
        """List secrets that need rotation"""
        logger.info(f"Listing secrets for project: {project_name}")
        
        secrets = []
        paginator = self.secrets_client.get_paginator('list_secrets')
        
        for page in paginator.paginate():
            for secret in page['SecretList']:
                secret_name = secret['Name']
                
                # Filter secrets for this project
                if project_name in secret_name:
                    # Check if rotation is enabled
                    if secret.get('RotationEnabled', False):
                        secrets.append(secret)
                        logger.info(f"Found rotatable secret: {secret_name}")
                    else:
                        logger.debug(f"Rotation not enabled for: {secret_name}")
        
        return secrets
    
    def check_rotation_needed(self, secret_name: str, max_age_days: int = 30) -> bool:
        """Check if secret needs rotation based on age"""
        try:
            response = self.secrets_client.describe_secret(SecretId=secret_name)
            
            last_rotated = response.get('LastRotatedDate')
            if not last_rotated:
                # Never rotated, use creation date
                last_rotated = response.get('CreatedDate')
            
            if last_rotated:
                age = datetime.now(timezone.utc) - last_rotated
                needs_rotation = age.days >= max_age_days
                
                logger.info(f"Secret {secret_name}: age={age.days} days, needs_rotation={needs_rotation}")
                return needs_rotation
            
            return True  # Rotate if we can't determine age
            
        except Exception as e:
            logger.error(f"Error checking rotation for {secret_name}: {e}")
            return False
    
    def rotate_database_credentials(self, secret_name: str) -> bool:
        """Rotate database credentials"""
        logger.info(f"Rotating database credentials: {secret_name}")
        
        try:
            # Get current secret
            current_secret = self.secrets_client.get_secret_value(SecretId=secret_name)
            current_data = json.loads(current_secret['SecretString'])
            
            # Generate new password
            new_password = self.generate_secure_password()
            
            # Create new secret version
            new_data = current_data.copy()
            new_data['password'] = new_password
            
            # Update secret with new version
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_data),
                Description=f"Rotated on {datetime.now(timezone.utc).isoformat()}"
            )
            
            logger.info(f"Database credentials rotated successfully: {secret_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate database credentials {secret_name}: {e}")
            return False
    
    def rotate_api_keys(self, secret_name: str) -> bool:
        """Rotate API keys"""
        logger.info(f"Rotating API keys: {secret_name}")
        
        try:
            # Get current secret
            current_secret = self.secrets_client.get_secret_value(SecretId=secret_name)
            current_data = json.loads(current_secret['SecretString'])
            
            # Generate new API keys
            new_data = {}
            for key, value in current_data.items():
                if 'key' in key.lower() or 'token' in key.lower():
                    new_data[key] = self.generate_api_key()
                else:
                    new_data[key] = value
            
            # Update secret with new version
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_data),
                Description=f"Rotated on {datetime.now(timezone.utc).isoformat()}"
            )
            
            logger.info(f"API keys rotated successfully: {secret_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate API keys {secret_name}: {e}")
            return False
    
    def rotate_jwt_secrets(self, secret_name: str) -> bool:
        """Rotate JWT signing secrets"""
        logger.info(f"Rotating JWT secrets: {secret_name}")
        
        try:
            # Generate new JWT secret
            new_jwt_secret = self.generate_jwt_secret()
            
            # Get current secret
            current_secret = self.secrets_client.get_secret_value(SecretId=secret_name)
            current_data = json.loads(current_secret['SecretString'])
            
            # Update JWT secret
            new_data = current_data.copy()
            new_data['jwt_secret'] = new_jwt_secret
            
            # Update secret
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_data),
                Description=f"JWT secret rotated on {datetime.now(timezone.utc).isoformat()}"
            )
            
            logger.info(f"JWT secrets rotated successfully: {secret_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate JWT secrets {secret_name}: {e}")
            return False
    
    def rotate_encryption_keys(self, secret_name: str) -> bool:
        """Rotate encryption keys"""
        logger.info(f"Rotating encryption keys: {secret_name}")
        
        try:
            # Generate new encryption key
            new_key = self.generate_encryption_key()
            
            # Get current secret
            current_secret = self.secrets_client.get_secret_value(SecretId=secret_name)
            current_data = json.loads(current_secret['SecretString'])
            
            # Update encryption key
            new_data = current_data.copy()
            new_data['encryption_key'] = new_key
            
            # Update secret
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_data),
                Description=f"Encryption key rotated on {datetime.now(timezone.utc).isoformat()}"
            )
            
            logger.info(f"Encryption keys rotated successfully: {secret_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate encryption keys {secret_name}: {e}")
            return False
    
    def update_lambda_environment_variables(self, function_names: List[str]) -> None:
        """Update Lambda environment variables after rotation"""
        logger.info("Updating Lambda environment variables...")
        
        for function_name in function_names:
            try:
                # Get current configuration
                response = self.lambda_client.get_function_configuration(
                    FunctionName=function_name
                )
                
                current_env = response.get('Environment', {}).get('Variables', {})
                
                # Update environment variables that reference rotated secrets
                updated_env = current_env.copy()
                updated_env['SECRETS_LAST_ROTATED'] = datetime.now(timezone.utc).isoformat()
                
                # Update function configuration
                self.lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Environment={'Variables': updated_env}
                )
                
                logger.info(f"Updated environment variables for {function_name}")
                
            except Exception as e:
                logger.error(f"Failed to update environment variables for {function_name}: {e}")
    
    def notify_rotation_completion(self, rotated_secrets: List[str], failed_secrets: List[str]) -> None:
        """Send notification about rotation completion"""
        logger.info("Sending rotation completion notification...")
        
        try:
            # Create notification message
            message = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'rotated_secrets': rotated_secrets,
                'failed_secrets': failed_secrets,
                'total_rotated': len(rotated_secrets),
                'total_failed': len(failed_secrets)
            }
            
            # Store notification in Parameter Store
            self.ssm_client.put_parameter(
                Name='/voice-assistant/secrets-rotation/last-run',
                Value=json.dumps(message),
                Type='String',
                Overwrite=True,
                Description='Last secrets rotation run results'
            )
            
            logger.info(f"Rotation completed: {len(rotated_secrets)} successful, {len(failed_secrets)} failed")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def generate_api_key(self, length: int = 64) -> str:
        """Generate a secure API key"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
        return api_key
    
    def generate_jwt_secret(self, length: int = 64) -> str:
        """Generate a JWT signing secret"""
        import secrets
        
        return secrets.token_urlsafe(length)
    
    def generate_encryption_key(self, length: int = 32) -> str:
        """Generate an encryption key"""
        import secrets
        
        return secrets.token_hex(length)
    
    def rotate_secret(self, secret_name: str, secret_type: str) -> bool:
        """Rotate a secret based on its type"""
        rotation_methods = {
            'database': self.rotate_database_credentials,
            'api_keys': self.rotate_api_keys,
            'jwt': self.rotate_jwt_secrets,
            'encryption': self.rotate_encryption_keys
        }
        
        method = rotation_methods.get(secret_type)
        if method:
            return method(secret_name)
        else:
            logger.warning(f"Unknown secret type: {secret_type}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Rotate secrets in AWS Secrets Manager')
    parser.add_argument('--project-name', default='voice-assistant-ai', help='Project name')
    parser.add_argument('--environment', default='all', help='Environment to rotate (or "all")')
    parser.add_argument('--secret-type', help='Specific secret type to rotate')
    parser.add_argument('--max-age-days', type=int, default=30, help='Maximum age before rotation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be rotated without doing it')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    try:
        # Initialize rotator
        rotator = SecretsRotator(region=args.region)
        
        # Get secrets for rotation
        secrets = rotator.list_secrets_for_rotation(args.project_name)
        
        if not secrets:
            logger.info("No secrets found for rotation")
            return
        
        rotated_secrets = []
        failed_secrets = []
        
        for secret in secrets:
            secret_name = secret['Name']
            
            # Filter by environment if specified
            if args.environment != 'all' and args.environment not in secret_name:
                continue
            
            # Check if rotation is needed
            if not rotator.check_rotation_needed(secret_name, args.max_age_days):
                logger.info(f"Skipping {secret_name} - rotation not needed")
                continue
            
            # Determine secret type from name
            secret_type = 'database'  # default
            if 'api' in secret_name.lower():
                secret_type = 'api_keys'
            elif 'jwt' in secret_name.lower():
                secret_type = 'jwt'
            elif 'encryption' in secret_name.lower():
                secret_type = 'encryption'
            
            # Filter by secret type if specified
            if args.secret_type and secret_type != args.secret_type:
                continue
            
            if args.dry_run:
                logger.info(f"[DRY RUN] Would rotate {secret_name} (type: {secret_type})")
                continue
            
            # Rotate the secret
            logger.info(f"Rotating {secret_name} (type: {secret_type})")
            
            if rotator.rotate_secret(secret_name, secret_type):
                rotated_secrets.append(secret_name)
            else:
                failed_secrets.append(secret_name)
        
        if not args.dry_run:
            # Update Lambda functions
            lambda_functions = [
                f"{args.project_name}-chatbot-{args.environment}",
                f"{args.project_name}-auth-{args.environment}",
                f"{args.project_name}-monitoring-{args.environment}"
            ]
            
            if args.environment == 'all':
                # Update all environments
                for env in ['dev', 'staging', 'prod']:
                    env_functions = [f.replace(args.environment, env) for f in lambda_functions]
                    rotator.update_lambda_environment_variables(env_functions)
            else:
                rotator.update_lambda_environment_variables(lambda_functions)
            
            # Send notification
            rotator.notify_rotation_completion(rotated_secrets, failed_secrets)
        
        # Output results
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'project_name': args.project_name,
            'environment': args.environment,
            'dry_run': args.dry_run,
            'rotated_secrets': rotated_secrets,
            'failed_secrets': failed_secrets,
            'total_processed': len(rotated_secrets) + len(failed_secrets)
        }
        
        with open('secrets-rotation-result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        if failed_secrets:
            logger.error(f"Some secrets failed to rotate: {failed_secrets}")
            exit(1)
        else:
            logger.info("All secrets rotated successfully")
        
    except Exception as e:
        logger.error(f"Secrets rotation failed: {e}")
        exit(1)


if __name__ == '__main__':
    main()
