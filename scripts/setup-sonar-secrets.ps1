# Setup SonarQube Secrets in AWS Secrets Manager
# This script helps you store SonarQube credentials securely in AWS

param(
    [Parameter(Mandatory=$true)]
    [string]$SonarToken,
    
    [Parameter(Mandatory=$false)]
    [string]$SecretName = "voice-assistant-ai/sonar-token",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1"
)

Write-Host "🔐 Setting up SonarQube secrets in AWS Secrets Manager..." -ForegroundColor Blue

# Check if AWS CLI is installed
try {
    $null = aws --version
    Write-Host "✅ AWS CLI is installed" -ForegroundColor Green
}
catch {
    Write-Host "❌ AWS CLI is not installed. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check if AWS is configured
try {
    $null = aws sts get-caller-identity
    Write-Host "✅ AWS credentials are configured" -ForegroundColor Green
}
catch {
    Write-Host "❌ AWS credentials not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Create or update the secret
Write-Host "📝 Storing SonarQube token in AWS Secrets Manager..." -ForegroundColor Blue

try {
    # Check if secret already exists
    $existingSecret = aws secretsmanager describe-secret --secret-id $SecretName --region $Region 2>$null
    
    if ($existingSecret) {
        Write-Host "🔄 Updating existing secret..." -ForegroundColor Yellow
        aws secretsmanager update-secret --secret-id $SecretName --secret-string $SonarToken --region $Region
        Write-Host "✅ Secret updated successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "🆕 Creating new secret..." -ForegroundColor Yellow
        aws secretsmanager create-secret --name $SecretName --secret-string $SonarToken --region $Region
        Write-Host "✅ Secret created successfully!" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Failed to store secret: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 SonarQube secrets setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Deploy your Terraform infrastructure: terraform apply"
Write-Host "2. The CodePipeline will now use the stored SonarQube token"
Write-Host "3. Monitor the pipeline execution in the AWS Console"
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "- View secret: aws secretsmanager get-secret-value --secret-id $SecretName --region $Region"
Write-Host "- Delete secret: aws secretsmanager delete-secret --secret-id $SecretName --region $Region"
Write-Host "- List secrets: aws secretsmanager list-secrets --region $Region"
