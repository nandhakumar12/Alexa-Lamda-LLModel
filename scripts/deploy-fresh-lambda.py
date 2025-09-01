#!/usr/bin/env python3
"""
Deploy the fresh Lambda function
"""

import boto3
import zipfile
import os
import json
import time

def create_lambda_zip():
    """Create deployment package for Lambda"""
    print("📦 CREATING LAMBDA DEPLOYMENT PACKAGE")
    print("=" * 50)
    
    zip_path = "fresh-lambda-deployment.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the Lambda function
        zipf.write("fresh-lambda/lambda_function.py", "lambda_function.py")
    
    print(f"✅ Created deployment package: {zip_path}")
    return zip_path

def deploy_lambda_function():
    """Deploy the Lambda function"""
    print("\n⚡ DEPLOYING LAMBDA FUNCTION")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = 'nandhakumar-fresh-chatbot'
    
    # Create IAM role for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = f"{function_name}-role"
    
    try:
        # Create role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for fresh chatbot Lambda function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_name}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print(f"✅ Attached basic execution policy")
        
        # Wait for role to be ready
        print("⏳ Waiting for IAM role to be ready...")
        time.sleep(10)
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        role_response = iam_client.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_name}")
    
    # Create deployment package
    zip_path = create_lambda_zip()
    
    try:
        # Read the zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Try to update existing function first
        try:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated existing Lambda function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Function doesn't exist, create it
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Fresh chatbot Lambda function without authentication',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'FUNCTION_TYPE': 'chatbot',
                        'VERSION': 'fresh'
                    }
                }
            )
            print(f"✅ Created new Lambda function: {function_name}")
        
        # Get function details
        function_info = lambda_client.get_function(FunctionName=function_name)
        function_arn = function_info['Configuration']['FunctionArn']
        
        print(f"✅ Lambda function ARN: {function_arn}")
        
        # Clean up zip file
        os.remove(zip_path)
        
        return function_name, function_arn
        
    except Exception as e:
        print(f"❌ Error deploying Lambda: {e}")
        return None, None

def test_lambda_function(function_name):
    """Test the Lambda function"""
    print(f"\n🧪 TESTING LAMBDA FUNCTION")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "message": "Hello! This is a test from the deployment script.",
            "session_id": "test-session"
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if payload.get('statusCode') == 200:
            body = json.loads(payload['body'])
            print(f"✅ Lambda test successful!")
            print(f"   Response: {body.get('response', 'No response')}")
            print(f"   Intent: {body.get('intent', 'No intent')}")
            return True
        else:
            print(f"❌ Lambda test failed: {payload}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lambda: {e}")
        return False

def main():
    """Main function"""
    print("🚨 DEPLOYING FRESH LAMBDA FUNCTION")
    print("=" * 60)
    
    function_name, function_arn = deploy_lambda_function()
    
    if function_name:
        success = test_lambda_function(function_name)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 LAMBDA DEPLOYMENT SUCCESSFUL!")
            print(f"\n📋 DETAILS:")
            print(f"   Function Name: {function_name}")
            print(f"   Function ARN: {function_arn}")
            print(f"   Runtime: Python 3.9")
            print(f"   Handler: lambda_function.lambda_handler")
            
            print(f"\n🎯 NEXT STEP: Create API Gateway")
            
            # Save function details for next step
            with open('lambda-details.json', 'w') as f:
                json.dump({
                    'function_name': function_name,
                    'function_arn': function_arn
                }, f, indent=2)
            
            print(f"✅ Saved function details to lambda-details.json")
            
        else:
            print("❌ LAMBDA DEPLOYMENT FAILED!")
    else:
        print("❌ LAMBDA DEPLOYMENT FAILED!")

if __name__ == "__main__":
    main()
