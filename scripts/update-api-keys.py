#!/usr/bin/env python3
"""
Update API Keys in AWS Secrets Manager
This script helps you update the API keys with real values
"""

import boto3
import json
import getpass
from typing import Dict, Any

def update_api_keys():
    """Update API keys in AWS Secrets Manager"""
    
    print("🔑 Updating API Keys in AWS Secrets Manager")
    print("=" * 50)
    
    # Initialize AWS client
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        print("✅ Connected to AWS Secrets Manager")
    except Exception as e:
        print(f"❌ Failed to connect to AWS: {e}")
        return False
    
    # Get current API keys
    try:
        response = client.get_secret_value(SecretId='voice-assistant-ai/api-keys')
        current_keys = json.loads(response['SecretString'])
        print(f"📋 Current API Keys: {list(current_keys.keys())}")
    except Exception as e:
        print(f"❌ Failed to get current API keys: {e}")
        return False
    
    # Collect new API keys
    new_keys = {}
    
    print("\n🔐 Enter your API keys (press Enter to keep current value):")
    
    # Claude API Key
    claude_key = input(f"Claude API Key [{current_keys.get('claude_api_key', 'N/A')}]: ").strip()
    if claude_key:
        new_keys['claude_api_key'] = claude_key
    else:
        new_keys['claude_api_key'] = current_keys.get('claude_api_key', 'YOUR_CLAUDE_API_KEY_HERE')
    
    # OpenAI API Key
    openai_key = input(f"OpenAI API Key [{current_keys.get('openai_api_key', 'N/A')}]: ").strip()
    if openai_key:
        new_keys['openai_api_key'] = openai_key
    else:
        new_keys['openai_api_key'] = current_keys.get('openai_api_key', 'YOUR_OPENAI_API_KEY_HERE')
    
    # Anthropic API Key
    anthropic_key = input(f"Anthropic API Key [{current_keys.get('anthropic_api_key', 'N/A')}]: ").strip()
    if anthropic_key:
        new_keys['anthropic_api_key'] = anthropic_key
    else:
        new_keys['anthropic_api_key'] = current_keys.get('anthropic_api_key', 'YOUR_ANTHROPIC_API_KEY_HERE')
    
    # Keep existing encryption key
    new_keys['encryption_key'] = current_keys.get('encryption_key', '')
    
    # Update the secret
    try:
        client.update_secret(
            SecretId='voice-assistant-ai/api-keys',
            SecretString=json.dumps(new_keys)
        )
        print("✅ Successfully updated API keys!")
        
        # Verify the update
        response = client.get_secret_value(SecretId='voice-assistant-ai/api-keys')
        updated_keys = json.loads(response['SecretString'])
        
        print("\n📋 Updated API Keys:")
        for key, value in updated_keys.items():
            if 'key' in key.lower():
                # Mask API keys for security
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update API keys: {e}")
        return False

def test_api_connection():
    """Test API connection with updated keys"""
    print("\n🧪 Testing API Connection...")
    
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId='voice-assistant-ai/api-keys')
        api_keys = json.loads(response['SecretString'])
        
        # Test Claude API (if available)
        if api_keys.get('claude_api_key') and api_keys['claude_api_key'] != 'YOUR_CLAUDE_API_KEY_HERE':
            print("✅ Claude API key is configured")
        else:
            print("⚠️  Claude API key not configured")
        
        # Test OpenAI API (if available)
        if api_keys.get('openai_api_key') and api_keys['openai_api_key'] != 'YOUR_OPENAI_API_KEY_HERE':
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️  OpenAI API key not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test API connection: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Voice Assistant AI - API Keys Update Tool")
    print("=" * 50)
    
    # Update API keys
    if update_api_keys():
        # Test connection
        test_api_connection()
        print("\n🎉 API Keys update completed successfully!")
    else:
        print("\n❌ API Keys update failed!")
