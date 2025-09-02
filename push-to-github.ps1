
# Voice Assistant AI - Push to GitHub Script
# This script helps push the fixed buildspec files to GitHub

Write-Host "=== Voice Assistant AI - Push to GitHub ===" -ForegroundColor Green
Write-Host ""

# Check if Git is available
try {
    git --version | Out-Null
    Write-Host "✓ Git is available" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not available. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Check if we're in a Git repository
if (-not (Test-Path ".git")) {
    Write-Host "✗ Not in a Git repository. Please navigate to your project directory." -ForegroundColor Red
    exit 1
}

Write-Host "✓ In a Git repository" -ForegroundColor Green

# Check current status
Write-Host ""
Write-Host "Checking Git status..." -ForegroundColor Cyan
git status

# Add the fixed buildspec files
Write-Host ""
Write-Host "Adding buildspec files..." -ForegroundColor Cyan
git add buildspec-deploy.yml
git add buildspec.yml
git add buildspec-test.yml
git add buildspec-security.yml
git add buildspec-terraform.yml
git add CI_CD_SETUP_GUIDE.md

# Check what will be committed
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git status --porcelain

# Ask for confirmation
Write-Host ""
$confirm = Read-Host "Do you want to commit and push these changes? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit 0
}

# Commit the changes
Write-Host ""
Write-Host "Committing changes..." -ForegroundColor Cyan
git commit -m "Fix YAML syntax errors in buildspec files and add CI/CD documentation

- Fixed YAML syntax issues in buildspec-deploy.yml
- Added comprehensive CI/CD setup guide
- Ensured all buildspec files have proper syntax
- Added production-grade pipeline configuration"

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "✓ Changes pushed to GitHub successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to AWS CodePipeline Console" -ForegroundColor White
Write-Host "2. Trigger the pipeline with 'Release change'" -ForegroundColor White
Write-Host "3. Monitor the build process" -ForegroundColor White
Write-Host "4. Check the build logs for any remaining issues" -ForegroundColor White
Write-Host ""
Write-Host "Pipeline URL: https://console.aws.amazon.com/codesuite/codepipeline/pipelines/voice-ai-pipeline/view" -ForegroundColor Cyan
t check
