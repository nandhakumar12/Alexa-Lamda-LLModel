#!/usr/bin/env python3
"""
Deploy Voice Assistant AI Frontend to S3
This script builds and deploys the React frontend to AWS S3
"""

import os
import subprocess
import boto3
import json
from pathlib import Path
from typing import Dict, Any

class FrontendDeployer:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.cloudfront_client = boto3.client('cloudfront')
        self.web_bucket = "voice-assistant-ai-prod-web-qay5floh"
        self.files_bucket = "voice-assistant-ai-prod-files-qay5floh"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if Node.js is installed
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found")
            return False
        
        # Check if npm is installed
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()}")
            else:
                print("❌ npm not found")
                return False
        except FileNotFoundError:
            print("❌ npm not found")
            return False
        
        # Check if frontend directory exists
        if not os.path.exists('frontend'):
            print("❌ Frontend directory not found")
            return False
        else:
            print("✅ Frontend directory found")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install frontend dependencies"""
        print("📦 Installing frontend dependencies...")
        
        try:
            os.chdir('frontend')
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
        finally:
            os.chdir('..')
    
    def build_frontend(self) -> bool:
        """Build the frontend for production"""
        print("🏗️ Building frontend for production...")
        
        try:
            os.chdir('frontend')
            
            # Set environment variables for production build
            env = os.environ.copy()
            env['REACT_APP_API_URL'] = 'https://7orgj957oe.execute-api.us-east-1.amazonaws.com/v1'
            env['REACT_APP_LLM_API_URL'] = 'https://ga551kmg0f.execute-api.us-east-1.amazonaws.com/prod/chat'
            env['REACT_APP_COGNITO_USER_POOL_ID'] = 'us-east-1_ID7e0JI2c'
            env['REACT_APP_COGNITO_CLIENT_ID'] = '4cnbjqiqk6lmg1f0lddhldglu4'
            env['REACT_APP_REGION'] = 'us-east-1'
            env['GENERATE_SOURCEMAP'] = 'false'
            env['CI'] = 'false'
            
            result = subprocess.run(['npm', 'run', 'build'], env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Frontend built successfully")
                return True
            else:
                print(f"❌ Build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            return False
        finally:
            os.chdir('..')
    
    def upload_to_s3(self) -> bool:
        """Upload built frontend to S3"""
        print("☁️ Uploading frontend to S3...")
        
        try:
            build_dir = Path('frontend/build')
            if not build_dir.exists():
                print("❌ Build directory not found")
                return False
            
            # Upload all files from build directory
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
                    
                    self.s3_client.upload_file(
                        str(file_path),
                        self.web_bucket,
                        s3_key,
                        ExtraArgs={
                            'ContentType': content_type,
                            'CacheControl': 'max-age=31536000' if file_path.suffix in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg'] else 'max-age=0'
                        }
                    )
                    print(f"  📄 Uploaded: {s3_key}")
            
            print("✅ Frontend uploaded to S3 successfully")
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
        """Deploy the frontend"""
        print("🚀 Deploying Voice Assistant AI Frontend")
        print("=" * 50)
        
        if not self.check_prerequisites():
            return False
        
        if not self.install_dependencies():
            return False
        
        if not self.build_frontend():
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
        print("3. Update API keys if needed")
        print("4. Configure custom domain (optional)")
        
        return True

def main():
    """Main function"""
    deployer = FrontendDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n✅ Frontend deployment completed successfully!")
    else:
        print("\n❌ Frontend deployment failed!")
    
    return success

if __name__ == "__main__":
    main()
