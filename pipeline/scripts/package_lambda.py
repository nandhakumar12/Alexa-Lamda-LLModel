#!/usr/bin/env python3
"""
Lambda Function Packaging and Deployment Script
Packages and deploys Lambda functions for Voice Assistant AI
"""

import os
import json
import zipfile
import argparse
import boto3
import hashlib
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LambdaPackager:
    """Handles Lambda function packaging and deployment"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
    def install_dependencies(self, function_dir: Path, target_dir: Path) -> None:
        """Install Python dependencies for Lambda function"""
        requirements_file = function_dir / 'requirements.txt'
        
        if requirements_file.exists():
            logger.info(f"Installing dependencies from {requirements_file}")
            
            # Install dependencies to target directory
            subprocess.run([
                'pip', 'install',
                '-r', str(requirements_file),
                '-t', str(target_dir),
                '--no-deps',
                '--platform', 'linux_x86_64',
                '--implementation', 'cp',
                '--python-version', '3.9',
                '--only-binary=:all:',
                '--upgrade'
            ], check=True)
            
            logger.info("Dependencies installed successfully")
        else:
            logger.info("No requirements.txt found, skipping dependency installation")
    
    def copy_source_code(self, function_dir: Path, target_dir: Path) -> None:
        """Copy source code to target directory"""
        logger.info(f"Copying source code from {function_dir}")
        
        # Copy Python files
        for py_file in function_dir.glob('*.py'):
            shutil.copy2(py_file, target_dir)
            logger.debug(f"Copied {py_file.name}")
        
        # Copy shared utilities if they exist
        shared_dir = function_dir.parent.parent / 'shared'
        if shared_dir.exists():
            target_shared = target_dir / 'shared'
            target_shared.mkdir(exist_ok=True)
            
            for py_file in shared_dir.glob('*.py'):
                shutil.copy2(py_file, target_shared)
                logger.debug(f"Copied shared/{py_file.name}")
    
    def create_deployment_package(self, function_dir: Path) -> Path:
        """Create deployment package for Lambda function"""
        function_name = function_dir.name
        logger.info(f"Creating deployment package for {function_name}")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package_dir = temp_path / 'package'
            package_dir.mkdir()
            
            # Install dependencies
            self.install_dependencies(function_dir, package_dir)
            
            # Copy source code
            self.copy_source_code(function_dir, package_dir)
            
            # Create ZIP file
            zip_path = function_dir / f'{function_name}.zip'
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in package_dir.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path
                        relative_path = file_path.relative_to(package_dir)
                        zip_file.write(file_path, relative_path)
                        logger.debug(f"Added {relative_path} to package")
            
            logger.info(f"Deployment package created: {zip_path}")
            return zip_path
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def upload_to_s3(self, zip_path: Path, bucket: str, key: str) -> str:
        """Upload deployment package to S3"""
        logger.info(f"Uploading {zip_path} to s3://{bucket}/{key}")
        
        self.s3_client.upload_file(str(zip_path), bucket, key)
        
        # Return S3 URL
        s3_url = f"s3://{bucket}/{key}"
        logger.info(f"Upload completed: {s3_url}")
        return s3_url
    
    def update_lambda_function(self, function_name: str, zip_path: Path, s3_bucket: str = None) -> Dict[str, Any]:
        """Update Lambda function code"""
        logger.info(f"Updating Lambda function: {function_name}")
        
        try:
            if s3_bucket:
                # Upload to S3 first
                s3_key = f"lambda-packages/{function_name}.zip"
                self.upload_to_s3(zip_path, s3_bucket, s3_key)
                
                # Update function code from S3
                response = self.lambda_client.update_function_code(
                    FunctionName=function_name,
                    S3Bucket=s3_bucket,
                    S3Key=s3_key
                )
            else:
                # Direct upload (for smaller packages)
                with open(zip_path, 'rb') as zip_file:
                    response = self.lambda_client.update_function_code(
                        FunctionName=function_name,
                        ZipFile=zip_file.read()
                    )
            
            logger.info(f"Function {function_name} updated successfully")
            return response
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            logger.error(f"Lambda function {function_name} not found")
            raise
        except Exception as e:
            logger.error(f"Failed to update function {function_name}: {e}")
            raise
    
    def wait_for_function_update(self, function_name: str, timeout: int = 300) -> None:
        """Wait for Lambda function update to complete"""
        logger.info(f"Waiting for function {function_name} to be updated...")
        
        waiter = self.lambda_client.get_waiter('function_updated')
        waiter.wait(
            FunctionName=function_name,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': timeout // 5
            }
        )
        
        logger.info(f"Function {function_name} update completed")
    
    def update_function_configuration(self, function_name: str, config: Dict[str, Any]) -> None:
        """Update Lambda function configuration"""
        logger.info(f"Updating configuration for {function_name}")
        
        update_params = {'FunctionName': function_name}
        
        # Add configuration parameters if provided
        if 'environment' in config:
            update_params['Environment'] = config['environment']
        
        if 'timeout' in config:
            update_params['Timeout'] = config['timeout']
        
        if 'memory_size' in config:
            update_params['MemorySize'] = config['memory_size']
        
        if 'description' in config:
            update_params['Description'] = config['description']
        
        if update_params:
            self.lambda_client.update_function_configuration(**update_params)
            logger.info(f"Configuration updated for {function_name}")
    
    def publish_version(self, function_name: str, description: str = None) -> str:
        """Publish a new version of the Lambda function"""
        logger.info(f"Publishing new version for {function_name}")
        
        response = self.lambda_client.publish_version(
            FunctionName=function_name,
            Description=description or f"Version published at {os.environ.get('CODEBUILD_BUILD_ID', 'manual')}"
        )
        
        version = response['Version']
        logger.info(f"Published version {version} for {function_name}")
        return version
    
    def update_alias(self, function_name: str, alias_name: str, version: str) -> None:
        """Update function alias to point to new version"""
        logger.info(f"Updating alias {alias_name} for {function_name} to version {version}")
        
        try:
            self.lambda_client.update_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=version
            )
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create alias if it doesn't exist
            self.lambda_client.create_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=version,
                Description=f"Alias for {alias_name} environment"
            )
        
        logger.info(f"Alias {alias_name} updated successfully")


def main():
    parser = argparse.ArgumentParser(description='Package and deploy Lambda functions')
    parser.add_argument('--function-dir', required=True, help='Lambda function directory')
    parser.add_argument('--function-name', help='Lambda function name (defaults to directory name)')
    parser.add_argument('--s3-bucket', help='S3 bucket for large packages')
    parser.add_argument('--environment', default='dev', help='Environment name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--publish-version', action='store_true', help='Publish new version')
    parser.add_argument('--update-alias', help='Update alias to new version')
    parser.add_argument('--config-file', help='JSON file with function configuration')
    
    args = parser.parse_args()
    
    try:
        function_dir = Path(args.function_dir)
        function_name = args.function_name or function_dir.name
        
        # Add environment suffix to function name
        full_function_name = f"voice-assistant-ai-{function_name}-{args.environment}"
        
        logger.info(f"Processing Lambda function: {full_function_name}")
        
        # Initialize packager
        packager = LambdaPackager(region=args.region)
        
        # Create deployment package
        zip_path = packager.create_deployment_package(function_dir)
        
        # Update function code
        response = packager.update_lambda_function(
            full_function_name, 
            zip_path, 
            args.s3_bucket
        )
        
        # Wait for update to complete
        packager.wait_for_function_update(full_function_name)
        
        # Update configuration if provided
        if args.config_file:
            with open(args.config_file, 'r') as f:
                config = json.load(f)
            packager.update_function_configuration(full_function_name, config)
        
        # Publish version if requested
        version = None
        if args.publish_version:
            version = packager.publish_version(full_function_name)
        
        # Update alias if requested
        if args.update_alias and version:
            packager.update_alias(full_function_name, args.update_alias, version)
        
        # Output results
        result = {
            'function_name': full_function_name,
            'code_sha256': response['CodeSha256'],
            'version': version or response['Version'],
            'last_modified': response['LastModified'],
            'status': 'success'
        }
        
        with open(f'{function_name}-deployment-result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Lambda function {full_function_name} deployed successfully")
        
        # Clean up
        zip_path.unlink()
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        
        # Output error result
        result = {
            'function_name': full_function_name if 'full_function_name' in locals() else 'unknown',
            'status': 'failed',
            'error': str(e)
        }
        
        with open(f'{function_name if "function_name" in locals() else "unknown"}-deployment-result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        exit(1)


if __name__ == '__main__':
    main()
