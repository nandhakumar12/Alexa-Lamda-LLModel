#!/usr/bin/env python3
"""
Quick AWS connection test before running the full deployment
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_connection():
    """Test AWS connection and credentials"""
    print("🔍 Testing AWS connection...")
    
    try:
        # Test STS (Security Token Service) to verify credentials
        sts_client = boto3.client('sts', region_name='us-east-1')
        identity = sts_client.get_caller_identity()
        
        print("✅ AWS credentials are valid!")
        print(f"Account ID: {identity.get('Account', 'Unknown')}")
        print(f"User ARN: {identity.get('Arn', 'Unknown')}")
        
        # Test basic service access
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        functions = lambda_client.list_functions(MaxItems=5)
        print(f"✅ Lambda access confirmed - Found {len(functions['Functions'])} functions")
        
        s3_client = boto3.client('s3', region_name='us-east-1')
        buckets = s3_client.list_buckets()
        print(f"✅ S3 access confirmed - Found {len(buckets['Buckets'])} buckets")
        
        apigateway_client = boto3.client('apigateway', region_name='us-east-1')
        apis = apigateway_client.get_rest_apis(limit=5)
        print(f"✅ API Gateway access confirmed - Found {len(apis['items'])} APIs")
        
        print("\n🎉 All AWS services are accessible! Ready for deployment.")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("Please configure AWS credentials using:")
        print("  aws configure")
        print("  or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        return False
        
    except ClientError as e:
        print(f"❌ AWS access error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_aws_connection()
