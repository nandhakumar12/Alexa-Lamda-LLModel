#!/usr/bin/env python3
"""
Setup AWS Secrets Manager for Voice Assistant AI
This script creates and populates all necessary secrets
"""

import boto3
import json
import secrets
import string
import sys
from typing import Dict, Any

def generate_random_string(length: int = 32, include_special: bool = True) -> str:
    """Generate a random string for secrets"""
    characters = string.ascii_letters + string.digits
    if include_special:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_secret(client, secret_name: str, secret_value: Dict[str, Any], description: str) -> bool:
    """Create or update a secret in AWS Secrets Manager"""
    try:
        # Check if secret exists
        try:
            client.describe_secret(SecretId=secret_name)
            print(f"📝 Updating existing secret: {secret_name}")
            # Update existing secret
            client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
        except client.exceptions.ResourceNotFoundException:
            print(f"🆕 Creating new secret: {secret_name}")
            # Create new secret
            client.create_secret(
                Name=secret_name,
                Description=description,
                SecretString=json.dumps(secret_value)
            )
        
        print(f"✅ Successfully configured secret: {secret_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring secret {secret_name}: {e}")
        return False

def main():
    """Main function to setup all secrets"""
    print("🔐 Setting up AWS Secrets Manager for Voice Assistant AI")
    print("=" * 60)
    
    # Initialize AWS client
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        print("✅ Connected to AWS Secrets Manager")
    except Exception as e:
        print(f"❌ Failed to connect to AWS: {e}")
        sys.exit(1)
    
    # Generate secrets
    jwt_secret = generate_random_string(64, True)
    encryption_key = generate_random_string(32, False)
    db_password = generate_random_string(16, True)
    
    # Define all secrets to create
    secrets_to_create = [
        {
            'name': 'voice-assistant-ai/jwt-secret',
            'description': 'JWT signing secret for user authentication',
            'value': jwt_secret
        },
        {
            'name': 'voice-assistant-ai/api-keys',
            'description': 'API keys and external service credentials',
            'value': {
                'claude_api_key': 'YOUR_CLAUDE_API_KEY_HERE',
                'openai_api_key': 'YOUR_OPENAI_API_KEY_HERE',
                'anthropic_api_key': 'YOUR_ANTHROPIC_API_KEY_HERE',
                'encryption_key': encryption_key
            }
        },
        {
            'name': 'voice-assistant-ai/database',
            'description': 'Database credentials for RDS (if used)',
            'value': {
                'username': 'admin',
                'password': db_password,
                'host': 'placeholder-host',
                'port': '5432',
                'database': 'voice_assistant_ai'
            }
        },
        {
            'name': 'voice-assistant-ai/app-config',
            'description': 'Application configuration and sensitive settings',
            'value': {
                'jwt_algorithm': 'HS256',
                'jwt_expiry_hours': 24,
                'max_tokens': 1000,
                'model_temperature': 0.7,
                'rate_limit_per_minute': 60,
                'session_timeout_minutes': 30
            }
        },
        {
            'name': 'voice-assistant-ai/external-services',
            'description': 'Third-party service credentials and webhooks',
            'value': {
                'slack_webhook_url': 'YOUR_SLACK_WEBHOOK_URL',
                'discord_webhook_url': 'YOUR_DISCORD_WEBHOOK_URL',
                'email_smtp_password': 'YOUR_EMAIL_SMTP_PASSWORD',
                'twilio_auth_token': 'YOUR_TWILIO_AUTH_TOKEN',
                'stripe_secret_key': 'YOUR_STRIPE_SECRET_KEY'
            }
        }
    ]
    
    # Create all secrets
    success_count = 0
    total_count = len(secrets_to_create)
    
    for secret_config in secrets_to_create:
        if create_secret(
            client,
            secret_config['name'],
            secret_config['value'],
            secret_config['description']
        ):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Secrets Setup Summary: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("🎉 All secrets configured successfully!")
        print("\n📋 Next Steps:")
        print("1. Update API keys in the 'voice-assistant-ai/api-keys' secret")
        print("2. Update external service credentials as needed")
        print("3. Deploy your Lambda functions to use the new secrets")
        print("4. Test the application to ensure secrets are working")
    else:
        print("⚠️  Some secrets failed to configure. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

