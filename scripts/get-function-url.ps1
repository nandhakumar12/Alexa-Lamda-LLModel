# Get Lambda Function URL
$functionUrl = aws lambda get-function-url-config --function-name voice-assistant-llm-chatbot --query FunctionUrl --output text 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Lambda Function URL: $functionUrl" -ForegroundColor Green
    
    # Test the Function URL
    Write-Host "Testing Function URL..." -ForegroundColor Yellow
    
    $testPayload = @{
        message = "Hello, test message"
        user_id = "test-user"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $functionUrl -Method POST -Body $testPayload -ContentType "application/json"
        Write-Host "SUCCESS! Function URL is working!" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Cyan
    } catch {
        Write-Host "Function URL test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Failed to get Function URL" -ForegroundColor Red
}
