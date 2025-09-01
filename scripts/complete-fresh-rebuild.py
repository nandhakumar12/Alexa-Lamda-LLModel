#!/usr/bin/env python3
"""
Complete Fresh Rebuild Script for Nandhakumar's AI Assistant
This script will:
1. Clean up all existing AWS resources
2. Create fresh production-grade infrastructure
3. Deploy with proper Claude LLM integration
4. Set up Cognito authentication
5. Deploy to CloudFront
"""

import boto3
import json
import time
import os
import zipfile
import requests
from botocore.exceptions import ClientError

class AIAssistantBuilder:
    def __init__(self):
        self.region = 'us-east-1'
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.apigateway_client = boto3.client('apigateway', region_name=self.region)
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.cloudfront_client = boto3.client('cloudfront', region_name=self.region)
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)
        self.iam_client = boto3.client('iam', region_name=self.region)
        
        # Configuration
        self.project_name = "nandhakumar-ai-assistant"
        self.bucket_name = f"{self.project_name}-frontend-{int(time.time())}"
        self.lambda_function_name = f"{self.project_name}-claude-llm"
        self.api_name = f"{self.project_name}-api"
        self.user_pool_name = f"{self.project_name}-users"
        
    def cleanup_existing_resources(self):
        """Clean up all existing resources"""
        print("🧹 Cleaning up existing resources...")
        
        # Delete Lambda functions
        try:
            functions = self.lambda_client.list_functions()['Functions']
            for func in functions:
                name = func['FunctionName']
                if any(keyword in name.lower() for keyword in ['voice-assistant', 'nandhakumar', 'chatbot', 'claude', 'ai-assistant']):
                    print(f"Deleting Lambda function: {name}")
                    try:
                        self.lambda_client.delete_function(FunctionName=name)
                    except Exception as e:
                        print(f"Error deleting {name}: {e}")
        except Exception as e:
            print(f"Error listing Lambda functions: {e}")
            
        # Delete API Gateways
        try:
            apis = self.apigateway_client.get_rest_apis()['items']
            for api in apis:
                name = api['name']
                if any(keyword in name.lower() for keyword in ['voice-assistant', 'nandhakumar', 'chatbot', 'claude', 'ai-assistant']):
                    print(f"Deleting API Gateway: {name}")
                    try:
                        self.apigateway_client.delete_rest_api(restApiId=api['id'])
                    except Exception as e:
                        print(f"Error deleting {name}: {e}")
        except Exception as e:
            print(f"Error listing API Gateways: {e}")
            
        # Delete S3 buckets
        try:
            buckets = self.s3_client.list_buckets()['Buckets']
            for bucket in buckets:
                name = bucket['Name']
                if any(keyword in name.lower() for keyword in ['voice-assistant', 'nandhakumar', 'chatbot', 'claude', 'ai-assistant']):
                    print(f"Deleting S3 bucket: {name}")
                    try:
                        # Delete all objects first
                        objects = self.s3_client.list_objects_v2(Bucket=name)
                        if 'Contents' in objects:
                            for obj in objects['Contents']:
                                self.s3_client.delete_object(Bucket=name, Key=obj['Key'])
                        self.s3_client.delete_bucket(Bucket=name)
                    except Exception as e:
                        print(f"Error deleting bucket {name}: {e}")
        except Exception as e:
            print(f"Error listing S3 buckets: {e}")
            
        # Delete Cognito User Pools
        try:
            pools = self.cognito_client.list_user_pools(MaxResults=60)['UserPools']
            for pool in pools:
                name = pool['Name']
                if any(keyword in name.lower() for keyword in ['voice-assistant', 'nandhakumar', 'chatbot', 'claude', 'ai-assistant']):
                    print(f"Deleting Cognito User Pool: {name}")
                    try:
                        self.cognito_client.delete_user_pool(UserPoolId=pool['Id'])
                    except Exception as e:
                        print(f"Error deleting pool {name}: {e}")
        except Exception as e:
            print(f"Error listing Cognito pools: {e}")
            
        print("✅ Cleanup completed!")
        time.sleep(5)  # Wait for resources to be fully deleted
        
    def create_iam_role(self):
        """Create IAM role for Lambda"""
        print("🔐 Creating IAM role...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        role_name = f"{self.project_name}-lambda-role"
        
        try:
            # Delete existing role if it exists
            try:
                self.iam_client.delete_role_policy(RoleName=role_name, PolicyName='LambdaExecutionPolicy')
            except:
                pass
            try:
                self.iam_client.detach_role_policy(RoleName=role_name, PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
            except:
                pass
            try:
                self.iam_client.delete_role(RoleName=role_name)
            except:
                pass
                
            # Create new role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Nandhakumar AI Assistant Lambda function'
            )
            
            # Attach basic execution policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Add custom policy for additional permissions
            custom_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:*"
                    }
                ]
            }
            
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='LambdaExecutionPolicy',
                PolicyDocument=json.dumps(custom_policy)
            )
            
            print("✅ IAM role created successfully!")
            time.sleep(10)  # Wait for role to propagate
            return response['Role']['Arn']
            
        except Exception as e:
            print(f"Error creating IAM role: {e}")
            return None

if __name__ == "__main__":
    builder = AIAssistantBuilder()
    
    print("🚀 Starting complete fresh rebuild of Nandhakumar's AI Assistant...")
    print("=" * 60)
    
    # Step 1: Cleanup
    builder.cleanup_existing_resources()
    
    # Step 2: Create IAM role
    role_arn = builder.create_iam_role()
    if not role_arn:
        print("❌ Failed to create IAM role. Exiting.")
        exit(1)
    
    print("🎉 Phase 1 completed! Ready for Lambda and API creation...")

    def create_lambda_function(self, role_arn):
        """Create Lambda function with Claude integration"""
        print("⚡ Creating Lambda function with Claude LLM...")

        # Lambda function code
        lambda_code = '''
import json
import boto3
import requests
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Production-grade Lambda function for Nandhakumar's AI Assistant
    Integrates with Claude 3 for intelligent responses
    """

    print(f"Received event: {json.dumps(event)}")

    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }

    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        # Parse request body
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = {}

        user_message = body.get('message', '').strip()
        user_name = body.get('userName', 'User')

        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Message is required',
                    'timestamp': datetime.now().isoformat()
                })
            }

        # Get Claude API key from environment
        claude_api_key = os.environ.get('CLAUDE_API_KEY')
        if not claude_api_key:
            print("WARNING: CLAUDE_API_KEY not found, using fallback response")
            response_text = get_fallback_response(user_message, user_name)
        else:
            response_text = get_claude_response(user_message, user_name, claude_api_key)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'user': user_name,
                'model': 'claude-3-sonnet' if claude_api_key else 'fallback'
            })
        }

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def get_claude_response(user_message, user_name, api_key):
    """Get response from Claude 3"""
    try:
        # Personalized system prompt for Nandhakumar
        system_prompt = f"""You are Nandhakumar's personal AI assistant. You are helpful, friendly, and knowledgeable.
        Always greet {user_name} warmly and provide thoughtful, personalized responses.
        You have a warm personality and enjoy discussing technology, music, and helping with various tasks.
        Keep responses conversational and engaging."""

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            print(f"Claude API error: {response.status_code} - {response.text}")
            return get_fallback_response(user_message, user_name)

    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return get_fallback_response(user_message, user_name)

def get_fallback_response(user_message, user_name):
    """Fallback responses when Claude API is not available"""

    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    music_keywords = ["music", "song", "artist", "album", "spotify", "playlist"]
    tech_keywords = ["technology", "coding", "programming", "ai", "machine learning", "aws"]

    message_lower = user_message.lower()

    if any(greeting in message_lower for greeting in greetings):
        return f"Hello {user_name}! I'm your AI assistant. How can I help you today? I'm here to assist with anything you need!"

    elif any(keyword in message_lower for keyword in music_keywords):
        return f"Hi {user_name}! I'd love to discuss music with you! While I'm experiencing some technical difficulties with my advanced AI, I'm still here to chat about your favorite artists, genres, or help you discover new music. What kind of music are you into?"

    elif any(keyword in message_lower for keyword in tech_keywords):
        return f"Great question about technology, {user_name}! I'm passionate about tech topics. Even though I'm having some technical issues with my main AI system, I can still help discuss programming, cloud computing, AI developments, and more. What specific tech topic interests you?"

    elif "who are you" in message_lower or "what are you" in message_lower:
        return f"I'm {user_name}'s personal AI assistant! I'm designed to be helpful, knowledgeable, and friendly. I can assist with various tasks, answer questions, and have engaging conversations. How can I help you today?"

    else:
        return f"Hi {user_name}! I understand you said: '{user_message}'. I'm currently experiencing some technical difficulties with my advanced AI, but I'm working to resolve them. How else can I help you today?"
'''

        # Create deployment package
        zip_filename = '/tmp/lambda_function.zip'
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)

        # Read the zip file
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()

        # Create Lambda function
        try:
            response = self.lambda_client.create_function(
                FunctionName=self.lambda_function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Production-grade AI Assistant for Nandhakumar with Claude LLM integration',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'CLAUDE_API_KEY': 'YOUR_CLAUDE_API_KEY_HERE'  # User needs to update this
                    }
                }
            )

            function_arn = response['FunctionArn']
            print(f"✅ Lambda function created: {function_arn}")

            # Wait for function to be ready
            time.sleep(5)
            return function_arn

        except Exception as e:
            print(f"Error creating Lambda function: {e}")
            return None

    def create_api_gateway(self, lambda_arn):
        """Create API Gateway with proper CORS and Lambda integration"""
        print("🌐 Creating API Gateway...")

        try:
            # Create REST API
            api_response = self.apigateway_client.create_rest_api(
                name=self.api_name,
                description='Production API for Nandhakumar AI Assistant',
                endpointConfiguration={'types': ['REGIONAL']}
            )

            api_id = api_response['id']
            print(f"✅ API Gateway created: {api_id}")

            # Get root resource
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            root_resource_id = None
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break

            # Create /chat resource
            chat_resource = self.apigateway_client.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='chat'
            )
            chat_resource_id = chat_resource['id']

            # Create OPTIONS method for CORS
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )

            # Set up OPTIONS integration
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={'application/json': '{"statusCode": 200}'}
            )

            # Set up OPTIONS method response
            self.apigateway_client.put_method_response(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': False,
                    'method.response.header.Access-Control-Allow-Methods': False,
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )

            # Set up OPTIONS integration response
            self.apigateway_client.put_integration_response(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )

            # Create POST method
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )

            # Set up Lambda integration
            lambda_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"

            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=chat_resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )

            # Add Lambda permission for API Gateway
            try:
                self.lambda_client.add_permission(
                    FunctionName=self.lambda_function_name,
                    StatementId='api-gateway-invoke',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=f"arn:aws:execute-api:{self.region}:*:{api_id}/*/*"
                )
            except Exception as e:
                print(f"Permission may already exist: {e}")

            # Deploy API
            self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod',
                description='Production deployment'
            )

            api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
            print(f"✅ API Gateway deployed: {api_url}")

            return {
                'api_id': api_id,
                'api_url': api_url,
                'chat_endpoint': f"{api_url}/chat"
            }

        except Exception as e:
            print(f"Error creating API Gateway: {e}")
            return None

    def create_cognito_user_pool(self):
        """Create Cognito User Pool for authentication"""
        print("👤 Creating Cognito User Pool...")

        try:
            # Create User Pool
            user_pool = self.cognito_client.create_user_pool(
                PoolName=self.user_pool_name,
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8,
                        'RequireUppercase': True,
                        'RequireLowercase': True,
                        'RequireNumbers': True,
                        'RequireSymbols': False
                    }
                },
                AutoVerifiedAttributes=['email'],
                UsernameAttributes=['email'],
                Schema=[
                    {
                        'Name': 'email',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    },
                    {
                        'Name': 'name',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    }
                ]
            )

            user_pool_id = user_pool['UserPool']['Id']
            print(f"✅ User Pool created: {user_pool_id}")

            # Create User Pool Client
            client = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName=f"{self.project_name}-client",
                GenerateSecret=False,
                ExplicitAuthFlows=[
                    'ALLOW_USER_SRP_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH'
                ],
                SupportedIdentityProviders=['COGNITO'],
                CallbackURLs=[f'https://{self.bucket_name}.s3-website-{self.region}.amazonaws.com'],
                LogoutURLs=[f'https://{self.bucket_name}.s3-website-{self.region}.amazonaws.com'],
                AllowedOAuthFlows=['code'],
                AllowedOAuthScopes=['email', 'openid', 'profile'],
                AllowedOAuthFlowsUserPoolClient=True
            )

            client_id = client['UserPoolClient']['ClientId']
            print(f"✅ User Pool Client created: {client_id}")

            return {
                'user_pool_id': user_pool_id,
                'client_id': client_id,
                'region': self.region
            }

        except Exception as e:
            print(f"Error creating Cognito User Pool: {e}")
            return None

    def create_frontend_files(self, api_url, cognito_config):
        """Create production frontend files"""
        print("🎨 Creating frontend files...")

        # Create HTML file
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nandhakumar's AI Assistant</title>
    <script src="https://sdk.amazonaws.com/js/aws-sdk-2.1.24.min.js"></script>
    <script src="https://unpkg.com/amazon-cognito-identity-js@6.3.12/dist/amazon-cognito-identity.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}

        .status {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
        }}

        .auth-section {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}

        .auth-form {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .auth-form input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}

        .auth-form button {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}

        .auth-form button:hover {{
            background: #5a6fd8;
        }}

        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }}

        .messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
        }}

        .message {{
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }}

        .user-message {{
            background: #667eea;
            color: white;
            margin-left: auto;
        }}

        .bot-message {{
            background: white;
            border: 1px solid #e0e0e0;
        }}

        .input-section {{
            display: flex;
            gap: 10px;
        }}

        .input-section input {{
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
        }}

        .input-section button {{
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }}

        .input-section button:hover {{
            background: #5a6fd8;
        }}

        .footer {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}

        .social-links {{
            margin-top: 10px;
        }}

        .social-links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }}

        .hidden {{
            display: none;
        }}

        .loading {{
            opacity: 0.7;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Nandhakumar's AI Assistant</h1>
            <p>Your Personal AI Companion</p>
            <div class="status" id="status">● Online</div>
        </div>

        <div class="auth-section" id="authSection">
            <div class="auth-form">
                <input type="email" id="email" placeholder="Email" required>
                <input type="password" id="password" placeholder="Password" required>
                <button onclick="signIn()">Sign In</button>
                <button onclick="signUp()">Sign Up</button>
                <button onclick="signOut()" id="signOutBtn" class="hidden">Sign Out</button>
                <span id="userInfo" class="hidden"></span>
            </div>
        </div>

        <div class="chat-container" id="chatContainer" class="hidden">
            <div class="messages" id="messages">
                <div class="message bot-message">
                    Hello! I'm your AI assistant. Please sign in to start chatting!
                </div>
            </div>

            <div class="input-section">
                <input type="text" id="messageInput" placeholder="Type your message here..."
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <div class="footer">
            <div>Powered by Claude LLM • Production Grade • Session: prod_{int(time.time())}</div>
            <div class="social-links">
                <a href="https://github.com" target="_blank">GitHub</a>
                <a href="https://linkedin.com" target="_blank">LinkedIn</a>
                <a href="https://youtube.com" target="_blank">YouTube</a>
            </div>
        </div>
    </div>

    <script>
        // Configuration
        const CONFIG = {{
            API_URL: '{api_url}/chat',
            COGNITO_USER_POOL_ID: '{cognito_config["user_pool_id"]}',
            COGNITO_CLIENT_ID: '{cognito_config["client_id"]}',
            COGNITO_REGION: '{cognito_config["region"]}'
        }};

        // Initialize Cognito
        const poolData = {{
            UserPoolId: CONFIG.COGNITO_USER_POOL_ID,
            ClientId: CONFIG.COGNITO_CLIENT_ID
        }};
        const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

        let currentUser = null;
        let userName = 'User';

        // Check if user is already signed in
        window.onload = function() {{
            checkAuthState();
        }};

        function checkAuthState() {{
            currentUser = userPool.getCurrentUser();
            if (currentUser) {{
                currentUser.getSession((err, session) => {{
                    if (err) {{
                        console.log('Session error:', err);
                        showAuthSection();
                        return;
                    }};
                    if (session.isValid()) {{
                        currentUser.getUserAttributes((err, attributes) => {{
                            if (!err && attributes) {{
                                const nameAttr = attributes.find(attr => attr.Name === 'name');
                                userName = nameAttr ? nameAttr.Value : 'Nandhakumar';
                            }}
                            showChatSection();
                            addBotMessage(`Welcome back, ${{userName}}! I'm your AI assistant. How can I help you today?`);
                        }});
                    }} else {{
                        showAuthSection();
                    }}
                }});
            }} else {{
                showAuthSection();
            }}
        }}

        function signUp() {{
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {{
                alert('Please enter email and password');
                return;
            }}

            const attributeList = [
                new AmazonCognitoIdentity.CognitoUserAttribute({{
                    Name: 'email',
                    Value: email
                }}),
                new AmazonCognitoIdentity.CognitoUserAttribute({{
                    Name: 'name',
                    Value: 'Nandhakumar'
                }})
            ];

            userPool.signUp(email, password, attributeList, null, (err, result) => {{
                if (err) {{
                    alert('Sign up error: ' + err.message);
                    return;
                }}
                alert('Sign up successful! Please check your email for verification code.');
                const code = prompt('Enter verification code from email:');
                if (code) {{
                    result.user.confirmRegistration(code, true, (err, result) => {{
                        if (err) {{
                            alert('Verification error: ' + err.message);
                            return;
                        }}
                        alert('Account verified! You can now sign in.');
                    }});
                }}
            }});
        }}

        function signIn() {{
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {{
                alert('Please enter email and password');
                return;
            }}

            const authenticationData = {{
                Username: email,
                Password: password
            }};

            const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
            const userData = {{
                Username: email,
                Pool: userPool
            }};

            const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

            cognitoUser.authenticateUser(authenticationDetails, {{
                onSuccess: (result) => {{
                    currentUser = cognitoUser;
                    userName = 'Nandhakumar';
                    showChatSection();
                    addBotMessage(`Hello ${{userName}}! I'm your personal AI assistant. How can I help you today?`);
                }},
                onFailure: (err) => {{
                    alert('Sign in error: ' + err.message);
                }}
            }});
        }}

        function signOut() {{
            if (currentUser) {{
                currentUser.signOut();
                currentUser = null;
                userName = 'User';
                showAuthSection();
                document.getElementById('messages').innerHTML = '<div class="message bot-message">Hello! I\\'m your AI assistant. Please sign in to start chatting!</div>';
            }}
        }}

        function showAuthSection() {{
            document.getElementById('authSection').classList.remove('hidden');
            document.getElementById('chatContainer').classList.add('hidden');
            document.getElementById('signOutBtn').classList.add('hidden');
            document.getElementById('userInfo').classList.add('hidden');
        }}

        function showChatSection() {{
            document.getElementById('authSection').classList.add('hidden');
            document.getElementById('chatContainer').classList.remove('hidden');
            document.getElementById('signOutBtn').classList.remove('hidden');
            document.getElementById('userInfo').classList.remove('hidden');
            document.getElementById('userInfo').textContent = `Signed in as ${{userName}}`;
        }}

        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;
            if (!currentUser) {{
                alert('Please sign in first');
                return;
            }}

            // Add user message
            addUserMessage(message);
            input.value = '';

            // Show loading
            const container = document.querySelector('.container');
            container.classList.add('loading');

            try {{
                const response = await fetch(CONFIG.API_URL, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        message: message,
                        userName: userName
                    }})
                }});

                const data = await response.json();

                if (response.ok) {{
                    addBotMessage(data.response);
                }} else {{
                    addBotMessage('Sorry, I encountered an error. Please try again.');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                addBotMessage('Sorry, I\\'m having trouble connecting. Please try again.');
            }} finally {{
                container.classList.remove('loading');
            }}
        }}

        function addUserMessage(message) {{
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message';
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        function addBotMessage(message) {{
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
    </script>
</body>
</html>'''

        return html_content

    def deploy_to_s3(self, html_content):
        """Deploy frontend to S3"""
        print("☁️ Deploying to S3...")

        try:
            # Create S3 bucket
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )

            print(f"✅ S3 bucket created: {self.bucket_name}")

            # Configure bucket for static website hosting
            self.s3_client.put_bucket_website(
                Bucket=self.bucket_name,
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
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }

            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )

            # Upload HTML file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='index.html',
                Body=html_content,
                ContentType='text/html'
            )

            website_url = f"http://{self.bucket_name}.s3-website-{self.region}.amazonaws.com"
            print(f"✅ Website deployed to S3: {website_url}")

            return {
                'bucket_name': self.bucket_name,
                'website_url': website_url
            }

        except Exception as e:
            print(f"Error deploying to S3: {e}")
            return None

    def create_cloudfront_distribution(self, s3_info):
        """Create CloudFront distribution for production deployment"""
        print("🌍 Creating CloudFront distribution...")

        try:
            distribution_config = {
                'CallerReference': str(int(time.time())),
                'Comment': f'CloudFront distribution for {self.project_name}',
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'S3Origin',
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
                            'Id': 'S3Origin',
                            'DomainName': f"{s3_info['bucket_name']}.s3.amazonaws.com",
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            }
                        }
                    ]
                },
                'Enabled': True,
                'DefaultRootObject': 'index.html',
                'PriceClass': 'PriceClass_100'
            }

            response = self.cloudfront_client.create_distribution(
                DistributionConfig=distribution_config
            )

            distribution_id = response['Distribution']['Id']
            domain_name = response['Distribution']['DomainName']
            cloudfront_url = f"https://{domain_name}"

            print(f"✅ CloudFront distribution created: {cloudfront_url}")
            print(f"Distribution ID: {distribution_id}")
            print("⏳ CloudFront deployment may take 10-15 minutes to fully propagate")

            return {
                'distribution_id': distribution_id,
                'domain_name': domain_name,
                'cloudfront_url': cloudfront_url
            }

        except Exception as e:
            print(f"Error creating CloudFront distribution: {e}")
            return None

    def run_complete_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Starting complete fresh rebuild of Nandhakumar's AI Assistant...")
        print("=" * 60)

        # Step 1: Cleanup
        self.cleanup_existing_resources()

        # Step 2: Create IAM role
        print("\n" + "=" * 60)
        role_arn = self.create_iam_role()
        if not role_arn:
            print("❌ Failed to create IAM role. Exiting.")
            return False

        # Step 3: Create Lambda function
        print("\n" + "=" * 60)
        lambda_arn = self.create_lambda_function(role_arn)
        if not lambda_arn:
            print("❌ Failed to create Lambda function. Exiting.")
            return False

        # Step 4: Create API Gateway
        print("\n" + "=" * 60)
        api_info = self.create_api_gateway(lambda_arn)
        if not api_info:
            print("❌ Failed to create API Gateway. Exiting.")
            return False

        # Step 5: Create Cognito User Pool
        print("\n" + "=" * 60)
        cognito_config = self.create_cognito_user_pool()
        if not cognito_config:
            print("❌ Failed to create Cognito User Pool. Exiting.")
            return False

        # Step 6: Create frontend
        print("\n" + "=" * 60)
        html_content = self.create_frontend_files(api_info['api_url'], cognito_config)

        # Step 7: Deploy to S3
        print("\n" + "=" * 60)
        s3_info = self.deploy_to_s3(html_content)
        if not s3_info:
            print("❌ Failed to deploy to S3. Exiting.")
            return False

        # Step 8: Create CloudFront distribution
        print("\n" + "=" * 60)
        cloudfront_info = self.create_cloudfront_distribution(s3_info)

        # Step 9: Summary
        print("\n" + "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        print(f"📱 S3 Website URL: {s3_info['website_url']}")
        if cloudfront_info:
            print(f"🌍 CloudFront URL: {cloudfront_info['cloudfront_url']}")
        print(f"🔗 API Endpoint: {api_info['chat_endpoint']}")
        print(f"👤 Cognito User Pool: {cognito_config['user_pool_id']}")
        print(f"⚡ Lambda Function: {self.lambda_function_name}")

        print("\n📋 NEXT STEPS:")
        print("1. Update Lambda environment variable CLAUDE_API_KEY with your actual API key")
        print("2. Test the authentication system by signing up")
        print("3. Start chatting with your AI assistant!")
        print("4. CloudFront may take 10-15 minutes to fully propagate")

        # Save configuration
        config = {
            'project_name': self.project_name,
            'api_url': api_info['api_url'],
            'chat_endpoint': api_info['chat_endpoint'],
            's3_website': s3_info['website_url'],
            'cloudfront_url': cloudfront_info['cloudfront_url'] if cloudfront_info else None,
            'cognito_user_pool_id': cognito_config['user_pool_id'],
            'cognito_client_id': cognito_config['client_id'],
            'lambda_function_name': self.lambda_function_name,
            'bucket_name': self.bucket_name
        }

        with open('deployment-config.json', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n💾 Configuration saved to deployment-config.json")
        return True

if __name__ == "__main__":
    try:
        builder = AIAssistantBuilder()
        success = builder.run_complete_deployment()

        if success:
            print("\n🎉 SUCCESS! Your AI Assistant is ready!")
            print("Check the URLs above to access your application.")
        else:
            print("\n❌ Deployment failed. Check the error messages above.")

    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your AWS credentials and try again.")
