# Fix API Gateway by creating deployment and stages
Write-Host "Fixing API Gateway deployment..." -ForegroundColor Cyan

$apiId = "7orgj957oe"

# Create a deployment
Write-Host "Creating API Gateway deployment..." -ForegroundColor Yellow
$deployment = aws apigateway create-deployment --rest-api-id $apiId --stage-name prod --stage-description "Production stage" --description "Production deployment" --output json 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment created successfully!" -ForegroundColor Green
    
    # Test the endpoints
    Write-Host "Testing endpoints..." -ForegroundColor Yellow
    
    $endpoints = @(
        "https://$apiId.execute-api.us-east-1.amazonaws.com/prod/chatbot",
        "https://$apiId.execute-api.us-east-1.amazonaws.com/prod/health"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            if ($endpoint -like "*health*") {
                $response = Invoke-RestMethod -Uri $endpoint -Method GET -TimeoutSec 10
                Write-Host "✓ $endpoint - Working!" -ForegroundColor Green
            } else {
                $testPayload = @{
                    message = "Hello test"
                    user_id = "test-user"
                } | ConvertTo-Json
                
                $response = Invoke-RestMethod -Uri $endpoint -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 10
                Write-Host "✓ $endpoint - Working!" -ForegroundColor Green
            }
        } catch {
            Write-Host "✗ $endpoint - Error: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
    }
    
} else {
    Write-Host "Failed to create deployment" -ForegroundColor Red
}

Write-Host "API Gateway fix complete!" -ForegroundColor Green
