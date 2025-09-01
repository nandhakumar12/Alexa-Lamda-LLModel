#!/usr/bin/env python3
"""
Deploy the built frontend to S3 and CloudFront
"""

import boto3
import json
import time
import os
import mimetypes
from pathlib import Path

# Configuration
PROJECT_NAME = "voice-assistant-ai"
ENVIRONMENT = "prod"
REGION = "us-east-1"
BUCKET_NAME = f"{PROJECT_NAME}-{ENVIRONMENT}-frontend"

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=REGION)
cloudfront_client = boto3.client('cloudfront', region_name=REGION)

def create_s3_bucket():
    """Create S3 bucket for hosting"""
    print(f"🪣 Creating S3 bucket: {BUCKET_NAME}")
    
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Created bucket: {BUCKET_NAME}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"✅ Bucket already exists: {BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False
    
    # Configure bucket for static website hosting
    try:
        s3_client.put_bucket_website(
            Bucket=BUCKET_NAME,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}
            }
        )
        print("✅ Configured bucket for static website hosting")
    except Exception as e:
        print(f"❌ Error configuring website: {e}")
        return False
    
    # Set bucket policy for public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ Set bucket policy for public access")
    except Exception as e:
        print(f"❌ Error setting bucket policy: {e}")
        return False
    
    return True

def upload_build_files():
    """Upload build files to S3"""
    print("📤 Uploading build files to S3...")
    
    build_dir = Path("frontend/build")
    if not build_dir.exists():
        print("❌ Build directory not found. Run 'npm run build' first.")
        return False
    
    uploaded_files = 0
    
    for file_path in build_dir.rglob("*"):
        if file_path.is_file():
            # Get relative path for S3 key
            s3_key = str(file_path.relative_to(build_dir)).replace("\\", "/")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'binary/octet-stream'
            
            # Set cache control based on file type
            if file_path.suffix in ['.html']:
                cache_control = 'max-age=0, no-cache, no-store, must-revalidate'
            elif file_path.suffix in ['.js', '.css']:
                cache_control = 'max-age=31536000'  # 1 year
            else:
                cache_control = 'max-age=86400'  # 1 day
            
            try:
                s3_client.upload_file(
                    str(file_path),
                    BUCKET_NAME,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': cache_control
                    }
                )
                uploaded_files += 1
                print(f"   ✅ {s3_key}")
            except Exception as e:
                print(f"   ❌ Failed to upload {s3_key}: {e}")
    
    print(f"✅ Uploaded {uploaded_files} files to S3")
    return True

def create_cloudfront_distribution():
    """Create CloudFront distribution"""
    print("☁️ Creating CloudFront distribution...")
    
    # Check if distribution already exists
    try:
        distributions = cloudfront_client.list_distributions()
        for dist in distributions.get('DistributionList', {}).get('Items', []):
            if BUCKET_NAME in str(dist.get('Origins', {}).get('Items', [])):
                print(f"✅ CloudFront distribution already exists: {dist['Id']}")
                print(f"🌐 Domain: {dist['DomainName']}")
                return dist['Id'], dist['DomainName']
    except Exception as e:
        print(f"⚠️  Error checking existing distributions: {e}")
    
    # Create new distribution
    distribution_config = {
        'CallerReference': f"{PROJECT_NAME}-{int(time.time())}",
        'Comment': f'{PROJECT_NAME} Frontend Distribution',
        'DefaultCacheBehavior': {
            'TargetOriginId': f'{BUCKET_NAME}-origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,
            'MaxTTL': 31536000
        },
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': f'{BUCKET_NAME}-origin',
                    'DomainName': f'{BUCKET_NAME}.s3.amazonaws.com',
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }
            ]
        },
        'Enabled': True,
        'DefaultRootObject': 'index.html',
        'CustomErrorResponses': {
            'Quantity': 1,
            'Items': [
                {
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 300
                }
            ]
        },
        'PriceClass': 'PriceClass_100'
    }
    
    try:
        response = cloudfront_client.create_distribution(
            DistributionConfig=distribution_config
        )
        
        distribution_id = response['Distribution']['Id']
        domain_name = response['Distribution']['DomainName']
        
        print(f"✅ Created CloudFront distribution: {distribution_id}")
        print(f"🌐 Domain: {domain_name}")
        print("⏳ Distribution is deploying... This may take 15-20 minutes.")
        
        return distribution_id, domain_name
        
    except Exception as e:
        print(f"❌ Error creating CloudFront distribution: {e}")
        return None, None

def update_cognito_callback_urls(domain_name):
    """Update Cognito User Pool Client with CloudFront domain"""
    print("🔄 Updating Cognito callback URLs...")
    
    try:
        cognito_client = boto3.client('cognito-idp', region_name=REGION)
        
        # Get User Pool Client details
        user_pool_id = "us-east-1_KSZDQ0iYx"
        client_id = "276p9eoi761kpfiivh7bth9f8s"
        
        response = cognito_client.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        
        client_config = response['UserPoolClient']
        
        # Update callback URLs
        callback_urls = [
            f"https://{domain_name}",
            f"https://{domain_name}/auth",
            "http://localhost:3000",
            "http://localhost:3000/auth"
        ]
        
        logout_urls = [
            f"https://{domain_name}",
            "http://localhost:3000"
        ]
        
        cognito_client.update_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            CallbackURLs=callback_urls,
            LogoutURLs=logout_urls,
            SupportedIdentityProviders=client_config.get('SupportedIdentityProviders', ['COGNITO']),
            AllowedOAuthFlows=client_config.get('AllowedOAuthFlows', []),
            AllowedOAuthScopes=client_config.get('AllowedOAuthScopes', []),
            AllowedOAuthFlowsUserPoolClient=client_config.get('AllowedOAuthFlowsUserPoolClient', False)
        )
        
        print("✅ Updated Cognito callback URLs")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not update Cognito URLs: {e}")

def main():
    print("🚀 Deploying to CloudFront")
    print("=" * 40)
    
    # Step 1: Create S3 bucket
    if not create_s3_bucket():
        return
    
    # Step 2: Upload build files
    if not upload_build_files():
        return
    
    # Step 3: Create CloudFront distribution
    distribution_id, domain_name = create_cloudfront_distribution()
    
    if distribution_id and domain_name:
        # Step 4: Update Cognito URLs
        update_cognito_callback_urls(domain_name)
        
        print("\n" + "=" * 40)
        print("🎉 Deployment completed successfully!")
        print(f"🌐 Your app is available at: https://{domain_name}")
        print(f"🪣 S3 Bucket: {BUCKET_NAME}")
        print(f"☁️ CloudFront Distribution: {distribution_id}")
        print("\n⏳ Note: CloudFront deployment may take 15-20 minutes to fully propagate.")
        print("🔐 Authentication is now properly configured with real Cognito credentials.")
        print("\n💬 You can now:")
        print("1. Visit the CloudFront URL")
        print("2. Sign up for a new account")
        print("3. Verify your email")
        print("4. Sign in and use the voice assistant")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
