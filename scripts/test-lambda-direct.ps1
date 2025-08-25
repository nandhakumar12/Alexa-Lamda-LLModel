# Test Lambda function directly
Write-Host "Testing Lambda function directly..." -ForegroundColor Cyan

$testPayload = @{
    message = "Hello! Can you help me with music?"
    user_id = "test-user"
} | ConvertTo-Json

Write-Host "Test payload: $testPayload" -ForegroundColor Yellow

# Test direct Lambda invocation
Write-Host "Invoking Lambda function directly..." -ForegroundColor Yellow
$result = aws lambda invoke --function-name voice-assistant-llm-chatbot --payload $testPayload response.json

if ($LASTEXITCODE -eq 0) {
    Write-Host "Lambda invocation successful!" -ForegroundColor Green
    if (Test-Path "response.json") {
        $response = Get-Content "response.json" | ConvertFrom-Json
        Write-Host "Response: $($response.body)" -ForegroundColor White
        Remove-Item "response.json" -Force
    }
} else {
    Write-Host "Lambda invocation failed" -ForegroundColor Red
}

# Try to get function URL
Write-Host "Checking for Function URL..." -ForegroundColor Yellow
$urlResult = aws lambda get-function-url-config --function-name voice-assistant-llm-chatbot 2>&1

if ($urlResult -like "*FunctionUrl*") {
    Write-Host "Function URL exists!" -ForegroundColor Green
    Write-Host $urlResult -ForegroundColor White
} else {
    Write-Host "No Function URL found" -ForegroundColor Red
}
