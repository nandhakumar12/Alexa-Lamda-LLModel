# Test the actual web application
Write-Host "Testing Voice Assistant Web Application..." -ForegroundColor Cyan

# Get the CloudFront URL
$cloudFrontUrl = "https://d3hl87po6y2b5n.cloudfront.net"

Write-Host "Web App URL: $cloudFrontUrl" -ForegroundColor Green
Write-Host ""
Write-Host "TESTING INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Open your browser and go to: $cloudFrontUrl" -ForegroundColor White
Write-Host "2. Toggle 'LLM Mode' ON (should show green)" -ForegroundColor White
Write-Host "3. Try saying: 'Hello! Can you help me with music?'" -ForegroundColor White
Write-Host "4. Look for intelligent responses about your music library" -ForegroundColor White
Write-Host ""
Write-Host "WHAT TO EXPECT:" -ForegroundColor Cyan
Write-Host "LLM Mode ON: Intelligent, personalized responses from Claude Haiku" -ForegroundColor Green
Write-Host "LLM Mode OFF: Basic rule-based responses" -ForegroundColor Yellow
Write-Host ""
Write-Host "If LLM responses aren't working, the fallback chatbot will still work!" -ForegroundColor Blue

# Test if the web app is accessible
try {
    $response = Invoke-WebRequest -Uri $cloudFrontUrl -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "Web application is accessible!" -ForegroundColor Green
    }
} catch {
    Write-Host "Web application may not be accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Ready to test! Open the URL above in your browser." -ForegroundColor Green
