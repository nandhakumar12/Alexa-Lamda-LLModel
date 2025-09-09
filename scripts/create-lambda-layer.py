#!/usr/bin/env python3
"""
Create Lambda Layer with shared utilities including Secrets Manager helper
"""

import os
import shutil
import zipfile
import boto3
from pathlib import Path

def create_lambda_layer():
    """Create a Lambda layer with shared utilities"""
    
    print("📦 Creating Lambda Layer with shared utilities...")
    
    # Create layer directory structure
    layer_dir = Path("lambda-layer")
    python_dir = layer_dir / "python"
    
    # Clean up existing layer
    if layer_dir.exists():
        shutil.rmtree(layer_dir)
    
    # Create directories
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy shared utilities
    shared_files = [
        "backend/shared/secrets_manager.py",
        "backend/shared/logger.py"
    ]
    
    for file_path in shared_files:
        if os.path.exists(file_path):
            dest_path = python_dir / Path(file_path).name
            shutil.copy2(file_path, dest_path)
            print(f"✅ Copied {file_path} to layer")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Create requirements.txt for the layer
    requirements = [
        "boto3>=1.26.0",
        "botocore>=1.29.0"
    ]
    
    with open(python_dir / "requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    # Create zip file
    zip_path = "lambda-layer.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(layer_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created Lambda layer: {zip_path}")
    
    # Upload to S3 (optional)
    upload_to_s3 = input("Upload layer to S3? (y/n): ").lower().strip() == 'y'
    
    if upload_to_s3:
        try:
            s3_client = boto3.client('s3')
            bucket_name = input("Enter S3 bucket name: ").strip()
            
            if bucket_name:
                s3_key = f"lambda-layers/voice-assistant-ai-shared-utilities.zip"
                s3_client.upload_file(zip_path, bucket_name, s3_key)
                print(f"✅ Uploaded to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"❌ Failed to upload to S3: {e}")
    
    # Clean up
    shutil.rmtree(layer_dir)
    print("🧹 Cleaned up temporary files")
    
    return zip_path

if __name__ == "__main__":
    create_lambda_layer()

