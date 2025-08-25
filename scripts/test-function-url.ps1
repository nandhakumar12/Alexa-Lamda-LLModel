# Test Lambda Function URL with proper request format
$functionUrl = "https://inruktpo3noyouklcsq3psiipq0cllcn.lambda-url.us-east-1.on.aws/"

Write-Host "Testing Lambda Function URL: $functionUrl" -ForegroundColor Cyan

# Create proper request payload
$payload = @{
    message = "Hello! Can you help me with music?"
    user_id = "test-user"
} | ConvertTo-Json

Write-Host "Request payload: $payload" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $functionUrl -Method POST -Body $payload -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "SUCCESS! LLM Function URL is working!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor White
    
} catch {
    Write-Host "Function URL test failed:" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}
