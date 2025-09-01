# Deploy Production Chatbot Lambda Function
# This script packages and deploys the production-ready chatbot

Write-Host "🚀 Deploying Production Chatbot Lambda Function..." -ForegroundColor Green

# Configuration
$FUNCTION_NAME = "voice-assistant-ai-prod-chatbot"
$REGION = "us-east-1"
$LAMBDA_DIR = "backend/lambda_functions/chatbot_handler"

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

# Change to lambda directory
Push-Location $LAMBDA_DIR

# Create a clean deployment package
if (Test-Path "deployment.zip") {
    Remove-Item "deployment.zip" -Force
}

# Copy the production chatbot file as lambda_function.py
Copy-Item "production_chatbot.py" "lambda_function.py" -Force

# Create zip package
Compress-Archive -Path "lambda_function.py" -DestinationPath "deployment.zip" -Force

Write-Host "✅ Deployment package created" -ForegroundColor Green

# Deploy to AWS Lambda
Write-Host "🚀 Deploying to AWS Lambda..." -ForegroundColor Yellow

try {
    # Update function code
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://deployment.zip `
        --region $REGION

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green
        
        # Update environment variables
        Write-Host "🔧 Updating environment variables..." -ForegroundColor Yellow
        
        aws lambda update-function-configuration `
            --function-name $FUNCTION_NAME `
            --environment Variables="{ENVIRONMENT=prod,CONVERSATIONS_TABLE=voice-assistant-ai-prod-conversations}" `
            --region $REGION
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Environment variables updated!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Warning: Could not update environment variables" -ForegroundColor Yellow
        }
        
        # Test the function
        Write-Host "🧪 Testing the function..." -ForegroundColor Yellow
        
        $testPayload = @{
            body = @{
                message = "Hello"
                session_id = "test-session"
                type = "text"
            } | ConvertTo-Json
        } | ConvertTo-Json
        
        $testResult = aws lambda invoke `
            --function-name $FUNCTION_NAME `
            --payload $testPayload `
            --region $REGION `
            response.json
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Function test completed!" -ForegroundColor Green
            Write-Host "📄 Test response:" -ForegroundColor Cyan
            Get-Content "response.json" | ConvertFrom-Json | ConvertTo-Json -Depth 3
            Remove-Item "response.json" -Force
        } else {
            Write-Host "❌ Function test failed" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Failed to update Lambda function" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error deploying Lambda function: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    Remove-Item "deployment.zip" -Force -ErrorAction SilentlyContinue
    Remove-Item "lambda_function.py" -Force -ErrorAction SilentlyContinue
    Pop-Location
}

Write-Host ""
Write-Host "🎉 Production Chatbot Deployment Complete!" -ForegroundColor Green
Write-Host "📋 Function Name: $FUNCTION_NAME" -ForegroundColor Cyan
Write-Host "🌍 Region: $REGION" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Features Deployed:" -ForegroundColor Green
Write-Host "  • AWS Bedrock Claude 3 Haiku integration" -ForegroundColor White
Write-Host "  • Intelligent fallback responses" -ForegroundColor White
Write-Host "  • Proper error handling" -ForegroundColor White
Write-Host "  • Conversation logging to DynamoDB" -ForegroundColor White
Write-Host "  • Clean welcome messages (no error IDs)" -ForegroundColor White
Write-Host "  • Production-ready CORS headers" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test the chatbot in the web interface" -ForegroundColor White
Write-Host "  2. Verify authentication is working" -ForegroundColor White
Write-Host "  3. Check that error IDs are no longer showing" -ForegroundColor White
