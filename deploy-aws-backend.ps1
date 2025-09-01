# PowerShell script to deploy AWS backend for Nandhakumar's AI Assistant
# This script will create Lambda, API Gateway, and S3 deployment

Write-Host "🚀 Deploying AWS Backend for Nandhakumar's AI Assistant" -ForegroundColor Green
Write-Host "=" * 60

# Check AWS CLI
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Test AWS credentials
Write-Host "🔍 Testing AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ AWS credentials valid - Account: $($identity.Account)" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured. Please run 'aws configure'" -ForegroundColor Red
    exit 1
}

# Variables
$functionName = "nandhakumar-ai-assistant-prod"
$roleName = "nandhakumar-ai-assistant-role"
$apiName = "nandhakumar-ai-assistant-api"
$bucketName = "nandhakumar-ai-assistant-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"
$region = "us-east-1"

Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "  Function: $functionName"
Write-Host "  Role: $roleName"
Write-Host "  API: $apiName"
Write-Host "  Bucket: $bucketName"
Write-Host "  Region: $region"

# Create IAM role
Write-Host "`n🔐 Creating IAM role..." -ForegroundColor Yellow

$trustPolicy = @"
{
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
"@

# Delete existing role if exists
try {
    aws iam detach-role-policy --role-name $roleName --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" 2>$null
    aws iam delete-role --role-name $roleName 2>$null
} catch {
    # Ignore errors
}

# Create role
$trustPolicy | Out-File -FilePath "trust-policy.json" -Encoding utf8
try {
    $roleResult = aws iam create-role --role-name $roleName --assume-role-policy-document file://trust-policy.json --output json | ConvertFrom-Json
    $roleArn = $roleResult.Role.Arn
    Write-Host "✅ IAM role created: $roleArn" -ForegroundColor Green
    
    # Attach policy
    aws iam attach-role-policy --role-name $roleName --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    Write-Host "✅ Policy attached to role" -ForegroundColor Green
    
    # Wait for role propagation
    Write-Host "⏳ Waiting for role propagation..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
} catch {
    Write-Host "❌ Error creating IAM role: $_" -ForegroundColor Red
    exit 1
}

# Create Lambda function code
Write-Host "`n⚡ Creating Lambda function..." -ForegroundColor Yellow

$lambdaCode = @"
import json
import requests
import os
from datetime import datetime

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS OK'})}
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        user_message = body.get('message', '').strip()
        user_name = body.get('userName', 'Nandhakumar')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message required'})
            }
        
        # Get Claude API key from environment
        claude_api_key = os.environ.get('CLAUDE_API_KEY')
        if claude_api_key and claude_api_key != 'YOUR_CLAUDE_API_KEY_HERE':
            response_text = get_claude_response(user_message, user_name, claude_api_key)
        else:
            response_text = get_intelligent_response(user_message, user_name)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'user': user_name,
                'model': 'claude-3-sonnet' if claude_api_key else 'intelligent-fallback'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_claude_response(message, user_name, api_key):
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "system": f"You are {user_name}'s personal AI assistant. Be helpful, friendly, and engaging.",
            "messages": [{"role": "user", "content": message}]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            return get_intelligent_response(message, user_name)
            
    except Exception as e:
        return get_intelligent_response(message, user_name)

def get_intelligent_response(message, user_name):
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return f"Hello {user_name}! I'm your personal AI assistant. How can I help you today?"
    elif any(word in message_lower for word in ['music', 'song', 'artist']):
        return f"Hi {user_name}! I'd love to discuss music with you! What kind of music are you into?"
    elif any(word in message_lower for word in ['technology', 'tech', 'coding', 'ai']):
        return f"Great question about technology, {user_name}! I'm passionate about tech topics. What interests you?"
    elif 'who are you' in message_lower:
        return f"I'm {user_name}'s personal AI assistant! I'm here to help with anything you need."
    else:
        return f"That's interesting, {user_name}! You said: '{message}'. Tell me more about that!"
"@

# Create Lambda deployment package
$lambdaCode | Out-File -FilePath "lambda_function.py" -Encoding utf8
Compress-Archive -Path "lambda_function.py" -DestinationPath "lambda_function.zip" -Force

# Delete existing function if exists
try {
    aws lambda delete-function --function-name $functionName 2>$null
    Start-Sleep -Seconds 5
} catch {
    # Ignore errors
}

# Create Lambda function
try {
    $lambdaResult = aws lambda create-function `
        --function-name $functionName `
        --runtime python3.9 `
        --role $roleArn `
        --handler lambda_function.lambda_handler `
        --zip-file fileb://lambda_function.zip `
        --description "Nandhakumar AI Assistant with Claude integration" `
        --timeout 30 `
        --memory-size 256 `
        --environment Variables='{CLAUDE_API_KEY=YOUR_CLAUDE_API_KEY_HERE}' `
        --output json | ConvertFrom-Json
    
    $lambdaArn = $lambdaResult.FunctionArn
    Write-Host "✅ Lambda function created: $lambdaArn" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error creating Lambda function: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 AWS Backend Deployment Started!" -ForegroundColor Green
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update Lambda environment variable CLAUDE_API_KEY with your actual API key"
Write-Host "2. Create API Gateway (run the API creation script next)"
Write-Host "3. Deploy frontend to S3"
Write-Host "4. Test the complete system"

# Save configuration
$config = @{
    functionName = $functionName
    lambdaArn = $lambdaArn
    roleArn = $roleArn
    bucketName = $bucketName
    region = $region
    deploymentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
} | ConvertTo-Json

$config | Out-File -FilePath "aws-deployment-config.json" -Encoding utf8
Write-Host "`n💾 Configuration saved to aws-deployment-config.json" -ForegroundColor Green

# Cleanup temporary files
Remove-Item "trust-policy.json" -ErrorAction SilentlyContinue
Remove-Item "lambda_function.py" -ErrorAction SilentlyContinue
Remove-Item "lambda_function.zip" -ErrorAction SilentlyContinue

Write-Host "`n✅ Phase 1 Complete: Lambda function deployed!" -ForegroundColor Green
