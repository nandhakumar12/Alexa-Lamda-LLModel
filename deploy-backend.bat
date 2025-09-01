@echo off
echo 🚀 Deploying AWS Backend for Nandhakumar's AI Assistant
echo ============================================================

REM Check AWS CLI
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI not found. Please install AWS CLI first.
    pause
    exit /b 1
)

echo ✅ AWS CLI found

REM Test AWS credentials
echo 🔍 Testing AWS credentials...
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS credentials not configured. Please run 'aws configure'
    pause
    exit /b 1
)

echo ✅ AWS credentials valid

REM Variables
set FUNCTION_NAME=nandhakumar-ai-assistant-prod
set ROLE_NAME=nandhakumar-ai-assistant-role
set API_NAME=nandhakumar-ai-assistant-api
set REGION=us-east-1

echo 📋 Configuration:
echo   Function: %FUNCTION_NAME%
echo   Role: %ROLE_NAME%
echo   API: %API_NAME%
echo   Region: %REGION%

REM Create trust policy file
echo 🔐 Creating IAM role...
echo {> trust-policy.json
echo     "Version": "2012-10-17",>> trust-policy.json
echo     "Statement": [>> trust-policy.json
echo         {>> trust-policy.json
echo             "Effect": "Allow",>> trust-policy.json
echo             "Principal": {>> trust-policy.json
echo                 "Service": "lambda.amazonaws.com">> trust-policy.json
echo             },>> trust-policy.json
echo             "Action": "sts:AssumeRole">> trust-policy.json
echo         }>> trust-policy.json
echo     ]>> trust-policy.json
echo }>> trust-policy.json

REM Clean up existing role
aws iam detach-role-policy --role-name %ROLE_NAME% --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" >nul 2>&1
aws iam delete-role --role-name %ROLE_NAME% >nul 2>&1

REM Create IAM role
aws iam create-role --role-name %ROLE_NAME% --assume-role-policy-document file://trust-policy.json >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error creating IAM role
    pause
    exit /b 1
)

REM Attach policy
aws iam attach-role-policy --role-name %ROLE_NAME% --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
if %errorlevel% neq 0 (
    echo ❌ Error attaching policy
    pause
    exit /b 1
)

echo ✅ IAM role created successfully

REM Get role ARN
for /f "tokens=*" %%i in ('aws iam get-role --role-name %ROLE_NAME% --query "Role.Arn" --output text') do set ROLE_ARN=%%i
echo Role ARN: %ROLE_ARN%

echo ⏳ Waiting for role propagation...
timeout /t 15 /nobreak >nul

REM Create Lambda function code
echo ⚡ Creating Lambda function...

echo import json> lambda_function.py
echo import requests>> lambda_function.py
echo import os>> lambda_function.py
echo from datetime import datetime>> lambda_function.py
echo.>> lambda_function.py
echo def lambda_handler(event, context):>> lambda_function.py
echo     print(f"Event: {json.dumps(event)}")>> lambda_function.py
echo.>> lambda_function.py
echo     headers = {>> lambda_function.py
echo         'Access-Control-Allow-Origin': '*',>> lambda_function.py
echo         'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',>> lambda_function.py
echo         'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',>> lambda_function.py
echo         'Content-Type': 'application/json'>> lambda_function.py
echo     }>> lambda_function.py
echo.>> lambda_function.py
echo     if event.get('httpMethod') == 'OPTIONS':>> lambda_function.py
echo         return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS OK'})}>> lambda_function.py
echo.>> lambda_function.py
echo     try:>> lambda_function.py
echo         body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})>> lambda_function.py
echo         user_message = body.get('message', '').strip()>> lambda_function.py
echo         user_name = body.get('userName', 'Nandhakumar')>> lambda_function.py
echo.>> lambda_function.py
echo         if not user_message:>> lambda_function.py
echo             return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Message required'})}>> lambda_function.py
echo.>> lambda_function.py
echo         response_text = get_intelligent_response(user_message, user_name)>> lambda_function.py
echo.>> lambda_function.py
echo         return {>> lambda_function.py
echo             'statusCode': 200,>> lambda_function.py
echo             'headers': headers,>> lambda_function.py
echo             'body': json.dumps({>> lambda_function.py
echo                 'response': response_text,>> lambda_function.py
echo                 'timestamp': datetime.now().isoformat(),>> lambda_function.py
echo                 'user': user_name,>> lambda_function.py
echo                 'model': 'nandhakumar-ai'>> lambda_function.py
echo             })>> lambda_function.py
echo         }>> lambda_function.py
echo.>> lambda_function.py
echo     except Exception as e:>> lambda_function.py
echo         return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}>> lambda_function.py
echo.>> lambda_function.py
echo def get_intelligent_response(message, user_name):>> lambda_function.py
echo     message_lower = message.lower()>> lambda_function.py
echo.>> lambda_function.py
echo     if any(word in message_lower for word in ['hello', 'hi', 'hey']):>> lambda_function.py
echo         return f"Hello {user_name}! I'm your personal AI assistant. How can I help you today?">> lambda_function.py
echo     elif any(word in message_lower for word in ['music', 'song', 'artist']):>> lambda_function.py
echo         return f"Hi {user_name}! I'd love to discuss music with you! What kind of music are you into?">> lambda_function.py
echo     elif any(word in message_lower for word in ['technology', 'tech', 'coding', 'ai']):>> lambda_function.py
echo         return f"Great question about technology, {user_name}! What interests you?">> lambda_function.py
echo     elif 'who are you' in message_lower:>> lambda_function.py
echo         return f"I'm {user_name}'s personal AI assistant! I'm here to help with anything you need.">> lambda_function.py
echo     else:>> lambda_function.py
echo         return f"That's interesting, {user_name}! You said: '{message}'. Tell me more!">> lambda_function.py

REM Create ZIP file
powershell -Command "Compress-Archive -Path 'lambda_function.py' -DestinationPath 'lambda_function.zip' -Force"

REM Delete existing function
aws lambda delete-function --function-name %FUNCTION_NAME% >nul 2>&1

REM Create Lambda function
aws lambda create-function ^
    --function-name %FUNCTION_NAME% ^
    --runtime python3.9 ^
    --role %ROLE_ARN% ^
    --handler lambda_function.lambda_handler ^
    --zip-file fileb://lambda_function.zip ^
    --description "Nandhakumar AI Assistant" ^
    --timeout 30 ^
    --memory-size 256

if %errorlevel% neq 0 (
    echo ❌ Error creating Lambda function
    pause
    exit /b 1
)

echo ✅ Lambda function created successfully

REM Get Lambda ARN
for /f "tokens=*" %%i in ('aws lambda get-function --function-name %FUNCTION_NAME% --query "Configuration.FunctionArn" --output text') do set LAMBDA_ARN=%%i
echo Lambda ARN: %LAMBDA_ARN%

REM Save configuration
echo {> aws-config.json
echo     "functionName": "%FUNCTION_NAME%",>> aws-config.json
echo     "lambdaArn": "%LAMBDA_ARN%",>> aws-config.json
echo     "roleArn": "%ROLE_ARN%",>> aws-config.json
echo     "region": "%REGION%">> aws-config.json
echo }>> aws-config.json

echo.
echo 🎉 AWS Backend Deployment Complete!
echo ✅ Lambda function: %FUNCTION_NAME%
echo ✅ Configuration saved to aws-config.json
echo.
echo 📋 Next Steps:
echo 1. Create API Gateway
echo 2. Deploy frontend to S3
echo 3. Test the complete system

REM Cleanup
del trust-policy.json >nul 2>&1
del lambda_function.py >nul 2>&1
del lambda_function.zip >nul 2>&1

pause
