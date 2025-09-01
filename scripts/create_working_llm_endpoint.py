import boto3
import json
import zipfile
import os

# Create a simple CORS-enabled proxy for the LLM function
proxy_code = '''
import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Invoke the main LLM function
        response = lambda_client.invoke(
            FunctionName='voice-assistant-llm-chatbot',
            Payload=json.dumps({
                'body': json.dumps(body)
            })
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        
        # Return with CORS headers
        return {
            'statusCode': response_payload.get('statusCode', 200),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': response_payload.get('body', '{}')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'I apologize, but I encountered a technical issue. Please try again.'
            })
        }
'''

def create_proxy_function():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = 'voice-assistant-llm-proxy'
    
    try:
        # Create IAM role for the proxy function
        role_name = 'voice-assistant-llm-proxy-role'
        
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
        
        try:
            iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            print(f"✅ Created IAM role: {role_name}")
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"ℹ️ IAM role already exists: {role_name}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Create policy for invoking the main LLM function
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "lambda:InvokeFunction",
                    "Resource": "arn:aws:lambda:us-east-1:*:function:voice-assistant-llm-chatbot"
                }
            ]
        }
        
        policy_name = 'voice-assistant-llm-proxy-policy'
        try:
            iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            print(f"✅ Created IAM policy: {policy_name}")
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"ℹ️ IAM policy already exists: {policy_name}")
        
        # Get account ID for policy ARN
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
        
        # Attach the policy to the role
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )

        # Wait for IAM role to propagate
        print("⏳ Waiting for IAM role to propagate...")
        import time
        time.sleep(10)
        
        # Create the deployment package
        zip_path = 'llm_proxy.zip'
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr('lambda_function.py', proxy_code)
        
        # Read the zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        
        # Create or update the Lambda function
        try:
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Timeout=30,
                MemorySize=256
            )
            print(f"✅ Created Lambda function: {function_name}")
        except lambda_client.exceptions.ResourceConflictException:
            # Function exists, update it
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated Lambda function: {function_name}")
        
        # Create function URL
        try:
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE'
            )
            function_url = url_response['FunctionUrl']
            print(f"✅ Created function URL: {function_url}")
        except lambda_client.exceptions.ResourceConflictException:
            # URL exists, get it
            url_response = lambda_client.get_function_url_config(FunctionName=function_name)
            function_url = url_response['FunctionUrl']
            print(f"ℹ️ Function URL already exists: {function_url}")
        
        # Clean up
        os.remove(zip_path)
        
        return function_url
        
    except Exception as e:
        print(f"❌ Error creating proxy function: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Creating LLM proxy function with CORS support...")
    
    function_url = create_proxy_function()
    
    if function_url:
        print(f"\n🎉 LLM proxy function created successfully!")
        print(f"🔗 Function URL: {function_url}")
        
        # Test the proxy function
        print("\nTesting proxy function...")
        import requests
        
        payload = {
            'message': 'Hello! Test the LLM proxy function',
            'user_id': 'test-user',
            'conversation_id': 'test-proxy'
        }
        
        try:
            response = requests.post(function_url, json=payload, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! LLM Response: {data.get('message', 'No message')[:100]}...")
                    print(f"\n🎯 Working endpoint: {function_url}")
                    print("✅ This endpoint can be used in the frontend!")
                except:
                    print(f"✅ Success: {response.text[:100]}...")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test Error: {e}")
    else:
        print("\n❌ Failed to create proxy function")
