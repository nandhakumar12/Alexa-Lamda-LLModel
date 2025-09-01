# Final LLM Voice Assistant Test
Write-Host "🧠 Testing LLM Voice Assistant - Final Check" -ForegroundColor Cyan

# Test 1: Direct LLM Lambda Function
Write-Host "`n1. Testing LLM Lambda Function (Direct)..." -ForegroundColor Yellow
$testPayload = '{ "body": "{\"message\": \"Hello! Can you help me with music?\", \"user_id\": \"test-user\"}" }'
Set-Content -Path "test_llm.json" -Value $testPayload -Encoding Ascii

try {
    aws lambda invoke --function-name voice-assistant-llm-chatbot --payload fileb://test_llm.json response_llm.json | Out-Null
    $response = Get-Content "response_llm.json" | ConvertFrom-Json
    
    if ($response.statusCode -eq 200) {
        $responseBody = $response.body | ConvertFrom-Json
        Write-Host "✅ LLM Lambda: WORKING!" -ForegroundColor Green
        Write-Host "   Response: $($responseBody.message)" -ForegroundColor White
        Write-Host "   Model: $($responseBody.model)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ LLM Lambda: Error - $($response.body)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ LLM Lambda: Exception - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Proxy Lambda Function (API Gateway Backend)
Write-Host "`n2. Testing Proxy Lambda Function..." -ForegroundColor Yellow
$proxyPayload = '{ "body": "{\"message\": \"Hello! Can you help me with music?\", \"user_id\": \"test-user\"}" }'
Set-Content -Path "test_proxy.json" -Value $proxyPayload -Encoding Ascii

try {
    aws lambda invoke --function-name voice-assistant-ai-prod-chatbot --payload fileb://test_proxy.json response_proxy.json | Out-Null
    $response = Get-Content "response_proxy.json" | ConvertFrom-Json
    
    if ($response.statusCode -eq 200) {
        $responseBody = $response.body | ConvertFrom-Json
        Write-Host "✅ Proxy Lambda: WORKING!" -ForegroundColor Green
        Write-Host "   Response: $($responseBody.response)" -ForegroundColor White
        Write-Host "   Source: $($responseBody.source)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Proxy Lambda: Error - $($response.body)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Proxy Lambda: Exception - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: API Gateway Endpoint
Write-Host "`n3. Testing API Gateway Endpoint..." -ForegroundColor Yellow
$payload = @{ message = "Hello! Can you help me with music?"; user_id = "test-user" } | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/prod/chatbot" -Method POST -Body $payload -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ API Gateway: WORKING!" -ForegroundColor Green
    Write-Host "   Response: $($response.response)" -ForegroundColor White
} catch {
    Write-Host "❌ API Gateway: Error - $($_.Exception.Message)" -ForegroundColor Red
}

# Cleanup
Remove-Item "test_llm.json", "response_llm.json", "test_proxy.json", "response_proxy.json" -Force -ErrorAction SilentlyContinue

# Final Status
Write-Host "`n🎯 FINAL STATUS:" -ForegroundColor Cyan
Write-Host "🌐 Web App: https://d3hl87po6y2b5n.cloudfront.net" -ForegroundColor Green
Write-Host "🧠 LLM Mode: Toggle ON in the web app" -ForegroundColor Green
Write-Host "💡 Expected: Intelligent responses from Claude Haiku" -ForegroundColor Green

Write-Host "`n📝 How to Test:" -ForegroundColor Yellow
Write-Host "1. Open the web app URL above" -ForegroundColor White
Write-Host "2. Make sure 'LLM Mode' toggle is ON (green)" -ForegroundColor White
Write-Host "3. Type: 'Hello! Can you help me with music?'" -ForegroundColor White
Write-Host "4. You should get intelligent responses from Claude Haiku" -ForegroundColor White

Write-Host "`n💰 Cost Info:" -ForegroundColor Yellow
Write-Host "Model: Claude Haiku (cheapest option)" -ForegroundColor White
Write-Host "Expected cost: $1-5/month for normal usage" -ForegroundColor White
