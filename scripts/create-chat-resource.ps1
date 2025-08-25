# Create /chat resource for LLM API Gateway
$apiId = "jv3ikn4o1m"
Write-Host "Creating /chat resource for API Gateway: $apiId"

# Get root resource ID
$rootResourceId = aws apigateway get-resources --rest-api-id $apiId --query "items[?path=='/'].id" --output text 2>$null
Write-Host "Root resource ID: $rootResourceId"

# Create /chat resource
Write-Host "Creating /chat resource..."
$chatResourceId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootResourceId --path-part "chat" --query "id" --output text 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Chat resource created with ID: $chatResourceId"
    
    # Create POST method
    Write-Host "Creating POST method..."
    aws apigateway put-method --rest-api-id $apiId --resource-id $chatResourceId --http-method POST --authorization-type NONE 2>$null
    
    # Create integration with Lambda
    $lambdaArn = "arn:aws:lambda:us-east-1:266833219725:function:voice-assistant-llm-chatbot"
    Write-Host "Creating Lambda integration..."
    aws apigateway put-integration --rest-api-id $apiId --resource-id $chatResourceId --http-method POST --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$lambdaArn/invocations" 2>$null
    
    # Add Lambda permission
    Write-Host "Adding Lambda permission..."
    aws lambda add-permission --function-name voice-assistant-llm-chatbot --statement-id "AllowAPIGatewayInvoke-chat" --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:266833219725:$apiId/*/*" 2>$null
    
    # Create OPTIONS method for CORS
    Write-Host "Creating OPTIONS method for CORS..."
    aws apigateway put-method --rest-api-id $apiId --resource-id $chatResourceId --http-method OPTIONS --authorization-type NONE 2>$null
    
    # Create OPTIONS integration
    aws apigateway put-integration --rest-api-id $apiId --resource-id $chatResourceId --http-method OPTIONS --type MOCK --request-templates '{\"application/json\":\"{\\\"statusCode\\\": 200}\"}' 2>$null
    
    # Create OPTIONS method response
    aws apigateway put-method-response --rest-api-id $apiId --resource-id $chatResourceId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true' 2>$null
    
    # Create OPTIONS integration response
    aws apigateway put-integration-response --rest-api-id $apiId --resource-id $chatResourceId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=\"Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\",method.response.header.Access-Control-Allow-Methods=\"GET,OPTIONS,POST,PUT\",method.response.header.Access-Control-Allow-Origin=\"*\"' 2>$null
    
    # Deploy the API
    Write-Host "Deploying API..."
    aws apigateway create-deployment --rest-api-id $apiId --stage-name prod 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS! LLM endpoint created: https://$apiId.execute-api.us-east-1.amazonaws.com/prod/chat" -ForegroundColor Green
    } else {
        Write-Host "Deployment failed" -ForegroundColor Red
    }
} else {
    Write-Host "Failed to create chat resource" -ForegroundColor Red
}
