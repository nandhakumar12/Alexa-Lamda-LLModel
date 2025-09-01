#!/usr/bin/env python3
"""
Step 4: Create Cognito User Pool for authentication
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_cognito_user_pool():
    """Create Cognito User Pool for authentication"""
    print("👤 Creating Cognito User Pool...")
    
    region = 'us-east-1'
    cognito_client = boto3.client('cognito-idp', region_name=region)
    
    project_name = "nandhakumar-ai-assistant"
    user_pool_name = f"{project_name}-users"
    
    try:
        # Create User Pool
        user_pool = cognito_client.create_user_pool(
            PoolName=user_pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email'],
            UsernameAttributes=['email'],
            Schema=[
                {
                    'Name': 'email',
                    'AttributeDataType': 'String',
                    'Required': True,
                    'Mutable': True
                },
                {
                    'Name': 'name',
                    'AttributeDataType': 'String',
                    'Required': True,
                    'Mutable': True
                }
            ],
            VerificationMessageTemplate={
                'DefaultEmailOption': 'CONFIRM_WITH_CODE',
                'EmailMessage': 'Welcome to Nandhakumar\'s AI Assistant! Your verification code is {####}',
                'EmailSubject': 'Verify your account for Nandhakumar\'s AI Assistant'
            }
        )
        
        user_pool_id = user_pool['UserPool']['Id']
        print(f"✅ User Pool created: {user_pool_id}")
        
        # Create User Pool Client
        client = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=f"{project_name}-client",
            GenerateSecret=False,
            ExplicitAuthFlows=[
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH'
            ],
            SupportedIdentityProviders=['COGNITO'],
            AllowedOAuthFlows=['code'],
            AllowedOAuthScopes=['email', 'openid', 'profile'],
            AllowedOAuthFlowsUserPoolClient=True,
            PreventUserExistenceErrors='ENABLED'
        )
        
        client_id = client['UserPoolClient']['ClientId']
        print(f"✅ User Pool Client created: {client_id}")
        
        # Create a test user for Nandhakumar
        try:
            cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username='nandhakumar@example.com',
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': 'nandhakumar@example.com'
                    },
                    {
                        'Name': 'name',
                        'Value': 'Nandhakumar'
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ],
                TemporaryPassword='TempPass123!',
                MessageAction='SUPPRESS'
            )
            
            # Set permanent password
            cognito_client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username='nandhakumar@example.com',
                Password='Nandhakumar123!',
                Permanent=True
            )
            
            print("✅ Test user created:")
            print("   Email: nandhakumar@example.com")
            print("   Password: Nandhakumar123!")
            
        except Exception as e:
            print(f"⚠️ Could not create test user: {e}")
        
        # Save configuration
        config = {
            'user_pool_id': user_pool_id,
            'client_id': client_id,
            'region': region,
            'user_pool_name': user_pool_name,
            'test_user': {
                'email': 'nandhakumar@example.com',
                'password': 'Nandhakumar123!'
            }
        }
        
        with open('step4-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuration saved to step4-config.json")
        return config
        
    except Exception as e:
        print(f"❌ Error creating Cognito User Pool: {e}")
        return None

if __name__ == "__main__":
    try:
        print("🚀 Step 4: Create Cognito User Pool")
        print("=" * 50)
        
        cognito_config = create_cognito_user_pool()
        
        if cognito_config:
            print("\n✅ Step 4 completed successfully!")
            print(f"👤 User Pool ID: {cognito_config['user_pool_id']}")
            print(f"🔑 Client ID: {cognito_config['client_id']}")
            print("Next: Run step5-deploy-frontend.py")
        else:
            print("\n❌ Step 4 failed!")
            
    except Exception as e:
        print(f"\n❌ Error in Step 4: {e}")
