# Test CI/CD Pipeline Script
# This script helps test the voice assistant CI/CD pipeline

Write-Host "=== Voice Assistant AI - CI/CD Pipeline Test ===" -ForegroundColor Green

# Get pipeline details
$PIPELINE_NAME = "voice-ai-pipeline"
$REGION = "us-east-1"

Write-Host "Pipeline Name: $PIPELINE_NAME" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow

# Check if AWS CLI is available
try {
    aws --version | Out-Null
    Write-Host "✓ AWS CLI is available" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI is not available. Please install it first." -ForegroundColor Red
    exit 1
}

# Check pipeline status
Write-Host "`nChecking pipeline status..." -ForegroundColor Cyan
try {
    $pipelineStatus = aws codepipeline get-pipeline-state --name $PIPELINE_NAME --region $REGION
    Write-Host "✓ Pipeline found and accessible" -ForegroundColor Green
    Write-Host "Pipeline ARN: $(($pipelineStatus | ConvertFrom-Json).pipelineArn)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Failed to get pipeline status" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Manual trigger instructions
Write-Host "`n=== Manual Pipeline Trigger Instructions ===" -ForegroundColor Green
Write-Host "1. Go to AWS CodePipeline Console: https://console.aws.amazon.com/codesuite/codepipeline/pipelines" -ForegroundColor Cyan
Write-Host "2. Find pipeline: $PIPELINE_NAME" -ForegroundColor Cyan
Write-Host "3. Click on the pipeline name" -ForegroundColor Cyan
Write-Host "4. Click 'Release change' button" -ForegroundColor Cyan
Write-Host "5. Monitor the pipeline execution" -ForegroundColor Cyan

Write-Host "`n=== Alternative: Trigger via AWS CLI ===" -ForegroundColor Green
Write-Host "Run this command to trigger the pipeline:" -ForegroundColor Cyan
Write-Host "aws codepipeline start-pipeline-execution --name $PIPELINE_NAME --region $REGION" -ForegroundColor Yellow

Write-Host "`n=== Pipeline Monitoring ===" -ForegroundColor Green
Write-Host "Monitor pipeline execution at:" -ForegroundColor Cyan
Write-Host "https://console.aws.amazon.com/codesuite/codepipeline/pipelines/$PIPELINE_NAME/view" -ForegroundColor Yellow

Write-Host "`n=== Expected Pipeline Stages ===" -ForegroundColor Green
Write-Host "1. Source: Pull code from GitHub" -ForegroundColor Cyan
Write-Host "2. Build: Build and package application" -ForegroundColor Cyan
Write-Host "3. Deploy: Deploy to Lambda function" -ForegroundColor Cyan

Write-Host "`n=== Troubleshooting ===" -ForegroundColor Green
Write-Host "If pipeline fails:" -ForegroundColor Cyan
Write-Host "- Check GitHub connection status" -ForegroundColor Cyan
Write-Host "- Verify buildspec-deploy.yml exists in repository" -ForegroundColor Cyan
Write-Host "- Check CodeBuild logs for detailed error messages" -ForegroundColor Cyan
Write-Host "- Ensure all required files are present in the repository" -ForegroundColor Cyan

Write-Host "`nPipeline test script completed!" -ForegroundColor Green
