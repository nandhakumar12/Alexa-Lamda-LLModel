#!/usr/bin/env python3
"""
Auto-update API Keys in AWS Secrets Manager with placeholder values
This script updates API keys without requiring user input
"""

import boto3
import json
from typing import Dict, Any

def update_api_keys_auto():
    """Update API keys automatically with placeholder values"""
    
    print("🔑 Auto-updating API Keys in AWS Secrets Manager")
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
    
    # Update with placeholder values (user can update later with real keys)
    updated_keys = {
        'claude_api_key': 'YOUR_CLAUDE_API_KEY_HERE',
        'openai_api_key': 'YOUR_OPENAI_API_KEY_HERE',
        'anthropic_api_key': 'YOUR_ANTHROPIC_API_KEY_HERE',
        'encryption_key': current_keys.get('encryption_key', 'ul1kRFIZiKthRAzr6bhmcEmk21haUlLc')
    }
    
    # Update the secret
    try:
        client.update_secret(
            SecretId='voice-assistant-ai/api-keys',
            SecretString=json.dumps(updated_keys)
        )
        print("✅ API keys updated with placeholder values")
        print("📝 Note: Update with real API keys later using:")
        print("   python scripts/update-api-keys.py")
        
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

def main():
    """Main function"""
    print("🚀 Voice Assistant AI - Auto API Keys Update")
    print("=" * 50)
    
    if update_api_keys_auto():
        print("\n✅ API Keys auto-update completed successfully!")
        print("🔧 To update with real API keys later, run:")
        print("   python scripts/update-api-keys.py")
    else:
        print("\n❌ API Keys auto-update failed!")

if __name__ == "__main__":
    main()
