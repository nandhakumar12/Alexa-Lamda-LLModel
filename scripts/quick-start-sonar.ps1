# Quick Start SonarQube Script (PowerShell)
# This script provides a fast way to get SonarQube running locally

Write-Host "🚀 Quick Start SonarQube for Voice Assistant AI" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue
Write-Host ""

# Check if Docker is running
try {
    $null = docker info
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start SonarQube
Write-Host "📦 Starting SonarQube..." -ForegroundColor Blue
docker-compose -f docker-compose.sonar.yml up -d

Write-Host "⏳ Waiting for SonarQube to be ready..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes on first run..." -ForegroundColor Yellow

# Wait for SonarQube to be ready
$maxAttempts = 30
$attempt = 1

while ($attempt -le $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9000/api/system/status" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ SonarQube is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        # SonarQube not ready yet
    }
    
    Write-Host "⏳ Attempt $attempt/$maxAttempts - Still starting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    $attempt++
}

if ($attempt -gt $maxAttempts) {
    Write-Host "❌ SonarQube failed to start within 5 minutes" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose -f docker-compose.sonar.yml logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 SonarQube is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:9000 in your browser"
Write-Host "2. Login with admin/admin"
Write-Host "3. Change the default password"
Write-Host "4. Generate a token: User > My Account > Security"
Write-Host "5. Set the token: `$env:SONAR_TOKEN='your_token_here'"
Write-Host "6. Run analysis: .\scripts\setup-sonarqube.ps1"
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "- Stop SonarQube: docker-compose -f docker-compose.sonar.yml down"
Write-Host "- View logs: docker-compose -f docker-compose.sonar.yml logs -f"
Write-Host "- Run analysis: .\scripts\setup-sonarqube.ps1"
Write-Host ""
Write-Host "📚 For detailed setup, see: docs/SONARQUBE_SETUP.md" -ForegroundColor Cyan
