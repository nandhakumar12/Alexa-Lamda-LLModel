#!/usr/bin/env python3
"""
Step 1: Clean up existing AWS resources
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def cleanup_resources():
    """Clean up all existing resources"""
    print("🧹 Starting cleanup of existing resources...")
    
    region = 'us-east-1'
    lambda_client = boto3.client('lambda', region_name=region)
    apigateway_client = boto3.client('apigateway', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    cognito_client = boto3.client('cognito-idp', region_name=region)
    
    # Keywords to identify our resources
    keywords = ['voice-assistant', 'nandhakumar', 'chatbot', 'claude', 'ai-assistant']
    
    # Delete Lambda functions
    print("🔍 Checking Lambda functions...")
    try:
        functions = lambda_client.list_functions()['Functions']
        deleted_count = 0
        for func in functions:
            name = func['FunctionName']
            if any(keyword in name.lower() for keyword in keywords):
                print(f"  Deleting Lambda function: {name}")
                try:
                    lambda_client.delete_function(FunctionName=name)
                    deleted_count += 1
                except Exception as e:
                    print(f"    Error deleting {name}: {e}")
        print(f"✅ Deleted {deleted_count} Lambda functions")
    except Exception as e:
        print(f"❌ Error listing Lambda functions: {e}")
        
    # Delete API Gateways
    print("🔍 Checking API Gateways...")
    try:
        apis = apigateway_client.get_rest_apis()['items']
        deleted_count = 0
        for api in apis:
            name = api['name']
            if any(keyword in name.lower() for keyword in keywords):
                print(f"  Deleting API Gateway: {name}")
                try:
                    apigateway_client.delete_rest_api(restApiId=api['id'])
                    deleted_count += 1
                except Exception as e:
                    print(f"    Error deleting {name}: {e}")
        print(f"✅ Deleted {deleted_count} API Gateways")
    except Exception as e:
        print(f"❌ Error listing API Gateways: {e}")
        
    # Delete S3 buckets
    print("🔍 Checking S3 buckets...")
    try:
        buckets = s3_client.list_buckets()['Buckets']
        deleted_count = 0
        for bucket in buckets:
            name = bucket['Name']
            if any(keyword in name.lower() for keyword in keywords):
                print(f"  Deleting S3 bucket: {name}")
                try:
                    # Delete all objects first
                    objects = s3_client.list_objects_v2(Bucket=name)
                    if 'Contents' in objects:
                        for obj in objects['Contents']:
                            s3_client.delete_object(Bucket=name, Key=obj['Key'])
                    s3_client.delete_bucket(Bucket=name)
                    deleted_count += 1
                except Exception as e:
                    print(f"    Error deleting bucket {name}: {e}")
        print(f"✅ Deleted {deleted_count} S3 buckets")
    except Exception as e:
        print(f"❌ Error listing S3 buckets: {e}")
        
    # Delete Cognito User Pools
    print("🔍 Checking Cognito User Pools...")
    try:
        pools = cognito_client.list_user_pools(MaxResults=60)['UserPools']
        deleted_count = 0
        for pool in pools:
            name = pool['Name']
            if any(keyword in name.lower() for keyword in keywords):
                print(f"  Deleting Cognito User Pool: {name}")
                try:
                    cognito_client.delete_user_pool(UserPoolId=pool['Id'])
                    deleted_count += 1
                except Exception as e:
                    print(f"    Error deleting pool {name}: {e}")
        print(f"✅ Deleted {deleted_count} Cognito User Pools")
    except Exception as e:
        print(f"❌ Error listing Cognito pools: {e}")
        
    print("\n🎉 Cleanup completed!")
    print("Waiting 10 seconds for resources to be fully deleted...")
    time.sleep(10)
    
    return True

if __name__ == "__main__":
    try:
        print("🚀 Step 1: Cleanup existing resources")
        print("=" * 50)
        
        # Test AWS connection first
        sts_client = boto3.client('sts', region_name='us-east-1')
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS connection verified - Account: {identity.get('Account', 'Unknown')}")
        
        # Run cleanup
        success = cleanup_resources()
        
        if success:
            print("\n✅ Step 1 completed successfully!")
            print("Next: Run step2-create-lambda.py")
        else:
            print("\n❌ Step 1 failed!")
            
    except Exception as e:
        print(f"\n❌ Error in Step 1: {e}")
        print("Please check your AWS credentials and try again.")
