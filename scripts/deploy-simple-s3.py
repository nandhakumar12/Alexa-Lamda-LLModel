#!/usr/bin/env python3
"""
Simple S3 deployment with CloudFront
"""

import boto3
import json
import time
import os
import mimetypes
from pathlib import Path

# Configuration
BUCKET_NAME = "nandhakumar-voice-assistant-prod"
REGION = "us-east-1"

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=REGION)
cloudfront_client = boto3.client('cloudfront', region_name=REGION)

def create_and_configure_bucket():
    """Create and configure S3 bucket"""
    print(f"🪣 Setting up S3 bucket: {BUCKET_NAME}")
    
    try:
        # Create bucket
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Created bucket: {BUCKET_NAME}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"✅ Bucket already exists: {BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False
    
    try:
        # Disable block public access
        s3_client.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print("✅ Disabled block public access")
        
        # Wait a moment for the setting to take effect
        time.sleep(5)
        
        # Configure for static website hosting
        s3_client.put_bucket_website(
            Bucket=BUCKET_NAME,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}
            }
        )
        print("✅ Configured for static website hosting")
        
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
        
        s3_client.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ Set bucket policy for public access")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring bucket: {e}")
        return False

def upload_files():
    """Upload build files to S3"""
    print("📤 Uploading files to S3...")
    
    build_dir = Path("build")
    if not build_dir.exists():
        print("❌ Build directory not found")
        return False
    
    uploaded = 0
    
    for file_path in build_dir.rglob("*"):
        if file_path.is_file():
            s3_key = str(file_path.relative_to(build_dir)).replace("\\", "/")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'binary/octet-stream'
            
            # Set cache control
            if file_path.suffix == '.html':
                cache_control = 'max-age=0, no-cache'
            else:
                cache_control = 'max-age=31536000'
            
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
                uploaded += 1
                if uploaded % 10 == 0:
                    print(f"   Uploaded {uploaded} files...")
            except Exception as e:
                print(f"   ❌ Failed to upload {s3_key}: {e}")
    
    print(f"✅ Uploaded {uploaded} files")
    return True

def create_cloudfront():
    """Create CloudFront distribution"""
    print("☁️ Creating CloudFront distribution...")
    
    # Check if distribution exists
    try:
        distributions = cloudfront_client.list_distributions()
        for dist in distributions.get('DistributionList', {}).get('Items', []):
            origins = dist.get('Origins', {}).get('Items', [])
            for origin in origins:
                if BUCKET_NAME in origin.get('DomainName', ''):
                    domain = dist['DomainName']
                    print(f"✅ Found existing distribution: {domain}")
                    return domain
    except Exception as e:
        print(f"⚠️  Error checking distributions: {e}")
    
    # Create new distribution
    config = {
        'CallerReference': f"voice-assistant-{int(time.time())}",
        'Comment': 'Voice Assistant Frontend',
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3-origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {'Enabled': False, 'Quantity': 0},
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0
        },
        'Origins': {
            'Quantity': 1,
            'Items': [{
                'Id': 'S3-origin',
                'DomainName': f'{BUCKET_NAME}.s3.amazonaws.com',
                'S3OriginConfig': {'OriginAccessIdentity': ''}
            }]
        },
        'Enabled': True,
        'DefaultRootObject': 'index.html',
        'CustomErrorResponses': {
            'Quantity': 1,
            'Items': [{
                'ErrorCode': 404,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200'
            }]
        }
    }
    
    try:
        response = cloudfront_client.create_distribution(DistributionConfig=config)
        domain = response['Distribution']['DomainName']
        dist_id = response['Distribution']['Id']
        
        print(f"✅ Created CloudFront distribution")
        print(f"   ID: {dist_id}")
        print(f"   Domain: {domain}")
        
        return domain
        
    except Exception as e:
        print(f"❌ Error creating CloudFront: {e}")
        return None

def test_deployment(domain):
    """Test the deployment"""
    print(f"\n🧪 Testing deployment...")
    
    s3_url = f"http://{BUCKET_NAME}.s3-website-{REGION}.amazonaws.com"
    cloudfront_url = f"https://{domain}"
    
    print(f"🌐 S3 Website: {s3_url}")
    print(f"☁️ CloudFront: {cloudfront_url}")
    
    # Test S3 website
    try:
        import requests
        response = requests.get(s3_url, timeout=10)
        if response.status_code == 200:
            print("✅ S3 website is accessible")
        else:
            print(f"⚠️  S3 website returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  S3 website test failed: {e}")

def main():
    print("🚀 Deploying Voice Assistant to AWS")
    print("=" * 50)
    
    # Step 1: Setup bucket
    if not create_and_configure_bucket():
        return
    
    # Step 2: Upload files
    if not upload_files():
        return
    
    # Step 3: Create CloudFront
    domain = create_cloudfront()
    
    # Step 4: Test deployment
    test_deployment(domain if domain else "")
    
    print("\n" + "=" * 50)
    print("🎉 Deployment Complete!")
    
    s3_url = f"http://{BUCKET_NAME}.s3-website-{REGION}.amazonaws.com"
    
    print(f"🌐 Your app is available at:")
    print(f"   S3 Website: {s3_url}")
    if domain:
        print(f"   CloudFront: https://{domain}")
        print(f"   (CloudFront may take 15-20 minutes to fully deploy)")
    
    print(f"\n✅ Features:")
    print(f"   🔐 Real Cognito authentication")
    print(f"   🤖 Working chatbot with Lambda")
    print(f"   🎨 Beautiful UI with animations")
    print(f"   📱 Responsive design")
    
    print(f"\n💬 To use:")
    print(f"   1. Visit the URL above")
    print(f"   2. Click 'Get Started'")
    print(f"   3. Sign up with your email")
    print(f"   4. Verify your email")
    print(f"   5. Sign in and start chatting!")

if __name__ == "__main__":
    main()
