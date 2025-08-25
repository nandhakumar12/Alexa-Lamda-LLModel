# Test the enhanced chatbot with LLM integration
Write-Host "Testing Enhanced Chatbot with LLM Integration..." -ForegroundColor Cyan

$endpoints = @(
    "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/v1/chatbot",
    "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/chatbot",
    "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/prod/chatbot"
)

# Test payload
$payload = @{
    message = "Hello! Can you help me play some music?"
    user_id = "test-user"
} | ConvertTo-Json

Write-Host "Payload: $payload" -ForegroundColor Yellow

foreach ($endpoint in $endpoints) {
    Write-Host "Testing endpoint: $endpoint" -ForegroundColor Yellow

    try {
        $response = Invoke-RestMethod -Uri $endpoint -Method POST -Body $payload -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "SUCCESS! Enhanced chatbot is working!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor White
    
    # Check if it's using LLM (look for advanced response patterns)
    $message = $response.message
    if ($message -like "*Claude*" -or $message -like "*AI assistant*" -or $message.Length -gt 200) {
        Write-Host "✅ LLM Integration Working!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Using fallback responses (LLM may be unavailable)" -ForegroundColor Yellow
        }

        break  # Success, exit loop

    } catch {
        Write-Host "Endpoint failed: $($_.Exception.Response.StatusCode) - $($_.Exception.Message)" -ForegroundColor Red
    }
}
