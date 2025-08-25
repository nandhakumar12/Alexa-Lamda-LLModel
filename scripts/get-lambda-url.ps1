# Get Lambda Function URL
Write-Host "Getting Lambda Function URL..." -ForegroundColor Cyan

$result = aws lambda get-function-url-config --function-name voice-assistant-llm-chatbot --output json 2>$null | ConvertFrom-Json

if ($result -and $result.FunctionUrl) {
    Write-Host "Lambda Function URL: $($result.FunctionUrl)" -ForegroundColor Green

    # Test the URL
    Write-Host "Testing the URL..." -ForegroundColor Yellow
    try {
        $testPayload = @{
            message = "Hello! Can you help me with music?"
            user_id = "test-user"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri $result.FunctionUrl -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 15
        Write-Host "✓ Lambda URL is working!" -ForegroundColor Green
        Write-Host "Response: $($response.response)" -ForegroundColor White
    } catch {
        Write-Host "✗ Lambda URL test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "No Function URL found or error occurred" -ForegroundColor Red
}
