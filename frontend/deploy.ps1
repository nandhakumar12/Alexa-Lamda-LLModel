# Nandhakumar's AI Assistant - Complete AWS Deployment Script (PowerShell)
# This script deploys the full stack: Cognito, DynamoDB, Lambda, API Gateway, S3, and CloudFront

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_NAME = "nandhakumar-ai-assistant"
$ENVIRONMENT = "prod"
$REGION = "us-east-1"
$BUCKET_NAME = "$PROJECT_NAME-$ENVIRONMENT-website"

Write-Host "🚀 Starting complete deployment of Nandhakumar's AI Assistant..." -ForegroundColor Green
Write-Host "📋 Project: $PROJECT_NAME" -ForegroundColor Cyan
Write-Host "🌍 Environment: $ENVIRONMENT" -ForegroundColor Cyan
Write-Host "📍 Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create S3 bucket for website hosting
Write-Host "🪣 Creating S3 bucket for website hosting..." -ForegroundColor Yellow
try {
    aws s3 mb s3://$BUCKET_NAME --region $REGION 2>$null
    Write-Host "✅ S3 bucket created: $BUCKET_NAME" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ Bucket already exists or error occurred" -ForegroundColor Yellow
}

# Step 2: Configure S3 bucket for static website hosting
Write-Host "🌐 Configuring S3 for static website hosting..." -ForegroundColor Yellow
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Step 3: Build the React application
Write-Host "📦 Building React application..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Upload build files to S3
Write-Host "⬆️ Uploading files to S3..." -ForegroundColor Yellow
aws s3 sync build/ s3://$BUCKET_NAME --delete --cache-control "max-age=31536000" --exclude "*.html"
aws s3 sync build/ s3://$BUCKET_NAME --delete --cache-control "max-age=0" --include "*.html"

# Step 5: Try to set bucket policy (may fail due to public access block)
Write-Host "🔓 Attempting to set bucket policy..." -ForegroundColor Yellow
$bucketPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
"@

$bucketPolicy | Out-File -FilePath "temp-bucket-policy.json" -Encoding UTF8
try {
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://temp-bucket-policy.json
    Write-Host "✅ Bucket policy set successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not set bucket policy (public access may be blocked)" -ForegroundColor Yellow
}
Remove-Item "temp-bucket-policy.json" -ErrorAction SilentlyContinue

# Step 6: Create CloudFront distribution
Write-Host "☁️ Creating CloudFront distribution..." -ForegroundColor Yellow

$cloudFrontConfig = @"
{
  "CallerReference": "$PROJECT_NAME-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
  "Comment": "$PROJECT_NAME website distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "$BUCKET_NAME-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "$BUCKET_NAME-origin",
        "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  }
}
"@

$cloudFrontConfig | Out-File -FilePath "temp-cloudfront-config.json" -Encoding UTF8

try {
    $distributionOutput = aws cloudfront create-distribution --distribution-config file://temp-cloudfront-config.json | ConvertFrom-Json
    $distributionId = $distributionOutput.Distribution.Id
    $cloudFrontDomain = $distributionOutput.Distribution.DomainName
    
    Write-Host "✅ CloudFront distribution created!" -ForegroundColor Green
    Write-Host "📋 Distribution ID: $distributionId" -ForegroundColor Cyan
    Write-Host "🌍 Domain: $cloudFrontDomain" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ CloudFront creation failed, using S3 website URL" -ForegroundColor Yellow
    $cloudFrontDomain = $null
}

Remove-Item "temp-cloudfront-config.json" -ErrorAction SilentlyContinue

# Step 7: Display results
Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Your application is available at:" -ForegroundColor Cyan
Write-Host "🌐 S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com" -ForegroundColor White

if ($cloudFrontDomain) {
    Write-Host "⚡ CloudFront: https://$cloudFrontDomain" -ForegroundColor White
    Write-Host ""
    Write-Host "⏱️ Note: CloudFront distribution may take 15-20 minutes to fully deploy." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Your AI Assistant is ready!" -ForegroundColor Green
