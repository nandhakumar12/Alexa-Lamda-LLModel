#!/usr/bin/env python3
"""
Deploy Existing Frontend Build to S3
Uses the existing build directory to deploy to S3
"""

import os
import boto3
import json
from pathlib import Path
from typing import Dict, Any

class ExistingBuildDeployer:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.web_bucket = "voice-assistant-ai-prod-web-qay5floh"
        
    def check_build_exists(self) -> bool:
        """Check if build directory exists and has files"""
        print("🔍 Checking for existing build...")
        
        build_dir = Path('frontend/build')
        if not build_dir.exists():
            print("❌ Build directory not found")
            return False
        
        # Check for index.html
        index_file = build_dir / 'index.html'
        if not index_file.exists():
            print("❌ index.html not found in build directory")
            return False
        
        # Count files
        file_count = sum(1 for f in build_dir.rglob('*') if f.is_file())
        print(f"✅ Build directory found with {file_count} files")
        return True
    
    def upload_to_s3(self) -> bool:
        """Upload built frontend to S3"""
        print("☁️ Uploading frontend to S3...")
        
        try:
            build_dir = Path('frontend/build')
            
            # Upload all files from build directory
            uploaded_files = 0
            for file_path in build_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(build_dir)
                    s3_key = str(relative_path).replace('\\', '/')
                    
                    # Determine content type
                    content_type = 'text/html'
                    if file_path.suffix == '.js':
                        content_type = 'application/javascript'
                    elif file_path.suffix == '.css':
                        content_type = 'text/css'
                    elif file_path.suffix == '.json':
                        content_type = 'application/json'
                    elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        content_type = f'image/{file_path.suffix[1:]}'
                    elif file_path.suffix == '.ico':
                        content_type = 'image/x-icon'
                    
                    self.s3_client.upload_file(
                        str(file_path),
                        self.web_bucket,
                        s3_key,
                        ExtraArgs={
                            'ContentType': content_type,
                            'CacheControl': 'max-age=31536000' if file_path.suffix in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'] else 'max-age=0'
                        }
                    )
                    uploaded_files += 1
                    print(f"  📄 Uploaded: {s3_key}")
            
            print(f"✅ {uploaded_files} files uploaded to S3 successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading to S3: {e}")
            return False
    
    def configure_website(self) -> bool:
        """Configure S3 bucket for website hosting"""
        print("🌐 Configuring S3 website hosting...")
        
        try:
            # Enable website hosting
            self.s3_client.put_bucket_website(
                Bucket=self.web_bucket,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'index.html'}
                }
            )
            
            # Set bucket policy for public read access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.web_bucket}/*"
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=self.web_bucket,
                Policy=json.dumps(bucket_policy)
            )
            
            print("✅ Website hosting configured")
            return True
            
        except Exception as e:
            print(f"❌ Error configuring website: {e}")
            return False
    
    def get_website_url(self) -> str:
        """Get the website URL"""
        return f"http://{self.web_bucket}.s3-website-us-east-1.amazonaws.com"
    
    def deploy(self) -> bool:
        """Deploy the existing frontend build"""
        print("🚀 Deploying Existing Frontend Build")
        print("=" * 50)
        
        if not self.check_build_exists():
            return False
        
        if not self.upload_to_s3():
            return False
        
        if not self.configure_website():
            return False
        
        website_url = self.get_website_url()
        print("\n" + "=" * 50)
        print("🎉 Frontend Deployment Complete!")
        print("=" * 50)
        print(f"🌐 Website URL: {website_url}")
        print(f"📱 Open in browser: {website_url}")
        print("\n📋 Next Steps:")
        print("1. Open the website URL in your browser")
        print("2. Test the voice assistant functionality")
        print("3. Update API keys with real values when ready")
        
        return True

def main():
    """Main function"""
    deployer = ExistingBuildDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n✅ Frontend deployment completed successfully!")
    else:
        print("\n❌ Frontend deployment failed!")
    
    return success

if __name__ == "__main__":
    main()
