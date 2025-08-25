# Fix API Gateway CORS for LLM endpoint
Write-Host "Fixing API Gateway CORS for LLM endpoint..." -ForegroundColor Cyan

# Get API Gateway ID
$apiId = aws apigateway get-rest-apis --query "items[?name=='voice-assistant-llm-api'].id" --output text 2>$null
if (-not $apiId -or $apiId -eq "None") {
    Write-Host "LLM API Gateway not found" -ForegroundColor Red
    exit 1
}

Write-Host "Found API Gateway ID: $apiId" -ForegroundColor Green

# Get chat resource ID
$resourceId = aws apigateway get-resources --rest-api-id $apiId --query "items[?pathPart=='chat'].id" --output text 2>$null
if (-not $resourceId -or $resourceId -eq "None") {
    Write-Host "Chat resource not found" -ForegroundColor Red
    exit 1
}

Write-Host "Found chat resource ID: $resourceId" -ForegroundColor Green

# Check if OPTIONS method exists
$optionsMethod = aws apigateway get-method --rest-api-id $apiId --resource-id $resourceId --http-method OPTIONS 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating OPTIONS method for CORS..." -ForegroundColor Yellow
    
    # Create OPTIONS method
    aws apigateway put-method --rest-api-id $apiId --resource-id $resourceId --http-method OPTIONS --authorization-type NONE 2>$null
    
    # Create OPTIONS integration
    aws apigateway put-integration --rest-api-id $apiId --resource-id $resourceId --http-method OPTIONS --type MOCK --request-templates '{\"application/json\":\"{\\\"statusCode\\\": 200}\"}' 2>$null
    
    # Create OPTIONS method response
    aws apigateway put-method-response --rest-api-id $apiId --resource-id $resourceId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true' 2>$null
    
    # Create OPTIONS integration response
    aws apigateway put-integration-response --rest-api-id $apiId --resource-id $resourceId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=\"Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\",method.response.header.Access-Control-Allow-Methods=\"GET,OPTIONS,POST,PUT\",method.response.header.Access-Control-Allow-Origin=\"*\"' 2>$null
    
    Write-Host "OPTIONS method created" -ForegroundColor Green
} else {
    Write-Host "OPTIONS method already exists" -ForegroundColor Green
}

# Deploy the API
Write-Host "Deploying API changes..." -ForegroundColor Yellow
aws apigateway create-deployment --rest-api-id $apiId --stage-name prod 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "API Gateway deployment successful!" -ForegroundColor Green
    Write-Host "LLM Endpoint: https://$apiId.execute-api.us-east-1.amazonaws.com/prod/chat" -ForegroundColor Cyan
} else {
    Write-Host "API Gateway deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "API Gateway CORS fix complete!" -ForegroundColor Green
