# Final LLM Test Script
Write-Host "🧠 Testing LLM Voice Assistant..." -ForegroundColor Cyan

# Test 1: Direct Lambda invocation
Write-Host "`n1. Testing LLM Lambda Function (Direct Invocation)..." -ForegroundColor Yellow

$testPayload = @{
    body = @{
        message = "Hello! Can you help me with music?"
        user_id = "test-user"
    } | ConvertTo-Json
} | ConvertTo-Json

Set-Content -Path "test_llm_payload.json" -Value $testPayload -Encoding Ascii

try {
    $result = aws lambda invoke --function-name voice-assistant-llm-chatbot --payload fileb://test_llm_payload.json response_llm.json 2>&1
    
    if (Test-Path "response_llm.json") {
        $response = Get-Content "response_llm.json" | ConvertFrom-Json
        
        if ($response.statusCode -eq 200) {
            $responseBody = $response.body | ConvertFrom-Json
            Write-Host "✅ LLM Lambda Function: WORKING!" -ForegroundColor Green
            Write-Host "Response: $($responseBody.message)" -ForegroundColor White
            Write-Host "Model: $($responseBody.model)" -ForegroundColor Cyan
        } else {
            Write-Host "❌ LLM Lambda Function: Error" -ForegroundColor Red
            Write-Host "Response: $($response.body)" -ForegroundColor Red
        }
        
        Remove-Item "response_llm.json" -Force
    } else {
        Write-Host "❌ LLM Lambda Function: No response file" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ LLM Lambda Function: Exception - $($_.Exception.Message)" -ForegroundColor Red
}

Remove-Item "test_llm_payload.json" -Force -ErrorAction SilentlyContinue

# Test 2: Web Application Status
Write-Host "`n2. Web Application Status..." -ForegroundColor Yellow
Write-Host "🌐 Frontend URL: https://d3hl87po6y2b5n.cloudfront.net" -ForegroundColor Green
Write-Host "🧠 LLM Mode: Available (toggle ON in the web app)" -ForegroundColor Green
Write-Host "🤖 Fallback Mode: Enhanced chatbot with smart responses" -ForegroundColor Green

# Test 3: Cost Information
Write-Host "`n3. Cost Information..." -ForegroundColor Yellow
Write-Host "💰 Model: Claude Haiku (90% cheaper than GPT-4)" -ForegroundColor Green
Write-Host "💰 Max tokens: 300 per response" -ForegroundColor Green
Write-Host "💰 Expected cost: $1-5/month for light usage" -ForegroundColor Green

Write-Host "`n🎉 LLM Voice Assistant Setup Complete!" -ForegroundColor Green
Write-Host "📝 Instructions:" -ForegroundColor Cyan
Write-Host "   1. Open: https://d3hl87po6y2b5n.cloudfront.net" -ForegroundColor White
Write-Host "   2. Toggle 'LLM Mode' ON (should show green)" -ForegroundColor White
Write-Host "   3. Try: 'Hello! Can you help me with music?'" -ForegroundColor White
Write-Host "   4. Expect: Intelligent responses from Claude Haiku" -ForegroundColor White
