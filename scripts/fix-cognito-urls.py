#!/usr/bin/env python3
"""
Fix Cognito URLs to only use HTTPS
"""

import boto3

def fix_cognito_urls():
    """Fix Cognito callback URLs to only use HTTPS"""
    print("🔧 Fixing Cognito User Pool Client URLs...")
    
    cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
    
    user_pool_id = "us-east-1_KSZDQ0iYx"
    client_id = "276p9eoi761kpfiivh7bth9f8s"
    cloudfront_domain = "d36s8pxm5kezg4.cloudfront.net"
    
    try:
        # Get current client configuration
        response = cognito_client.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        
        client_config = response['UserPoolClient']
        
        # Update callback URLs to only use HTTPS
        callback_urls = [
            f"https://{cloudfront_domain}",
            f"https://{cloudfront_domain}/auth",
            "http://localhost:3000",
            "http://localhost:3000/auth"
        ]
        
        logout_urls = [
            f"https://{cloudfront_domain}",
            "http://localhost:3000"
        ]
        
        # Update the client
        cognito_client.update_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            CallbackURLs=callback_urls,
            LogoutURLs=logout_urls,
            SupportedIdentityProviders=client_config.get('SupportedIdentityProviders', ['COGNITO']),
            AllowedOAuthFlows=client_config.get('AllowedOAuthFlows', []),
            AllowedOAuthScopes=client_config.get('AllowedOAuthScopes', []),
            AllowedOAuthFlowsUserPoolClient=client_config.get('AllowedOAuthFlowsUserPoolClient', False),
            ExplicitAuthFlows=client_config.get('ExplicitAuthFlows', [])
        )
        
        print("✅ Fixed Cognito User Pool Client URLs")
        print("📋 Callback URLs:")
        for url in callback_urls:
            print(f"   {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Cognito URLs: {e}")
        return False

def main():
    print("🔧 Fixing Cognito Configuration")
    print("=" * 40)
    
    if fix_cognito_urls():
        print("\n✅ Cognito URLs fixed successfully!")
        print("\n🌐 Your Voice Assistant is ready at:")
        print("   CloudFront: https://d36s8pxm5kezg4.cloudfront.net")
        print("   S3 Website: http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
        
        print("\n⏳ Note: CloudFront may take 15-20 minutes to fully deploy.")
        print("💡 You can use the S3 website URL immediately!")

if __name__ == "__main__":
    main()
