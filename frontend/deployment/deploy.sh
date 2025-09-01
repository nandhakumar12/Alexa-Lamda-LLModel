#!/bin/bash

# Nandhakumar's AI Assistant - Complete AWS Deployment Script
# This script deploys the full stack: Cognito, DynamoDB, Lambda, API Gateway, S3, and CloudFront

set -e

# Configuration
PROJECT_NAME="nandhakumar-ai-assistant"
ENVIRONMENT="prod"
REGION="us-east-1"
BUCKET_NAME="$PROJECT_NAME-$ENVIRONMENT"
CLOUDFRONT_DISTRIBUTION_ID=""  # Will be set after first deployment

echo "🚀 Starting complete deployment of Nandhakumar's AI Assistant..."
echo "📋 Project: $PROJECT_NAME"
echo "🌍 Environment: $ENVIRONMENT"
echo "📍 Region: $REGION"
echo ""

# Step 1: Deploy AWS Infrastructure
echo "☁️ Deploying AWS Infrastructure..."

# Deploy IAM Roles first
echo "🔑 Deploying IAM Roles..."
aws cloudformation deploy \
  --template-file ../../backend/cloudformation/lambda-roles.yaml \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-iam-roles" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Deploy Cognito User Pool
echo "🔐 Deploying Cognito User Pool..."
aws cloudformation deploy \
  --template-file ../../backend/cloudformation/cognito.yaml \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-cognito" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Deploy DynamoDB Tables
echo "🗄️ Deploying DynamoDB Tables..."
aws cloudformation deploy \
  --template-file ../../backend/cloudformation/dynamodb.yaml \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-dynamodb" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --region $REGION

# Get Cognito outputs
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-cognito" \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text --region $REGION)

USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-cognito" \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text --region $REGION)

USER_POOL_ARN=$(aws cloudformation describe-stacks \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-cognito" \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolArn`].OutputValue' \
  --output text --region $REGION)

echo "✅ Cognito User Pool ID: $USER_POOL_ID"
echo "✅ Cognito Client ID: $USER_POOL_CLIENT_ID"

# Step 2: Deploy Lambda Functions
echo "⚡ Deploying Lambda Functions..."

# Package and deploy AI Chat Lambda
cd ../../backend/lambda/ai-chat
zip -r ai-chat-lambda.zip . -x "*.git*" "node_modules/*"

AI_CHAT_FUNCTION_NAME="$PROJECT_NAME-$ENVIRONMENT-ai-chat"
aws lambda create-function \
  --function-name $AI_CHAT_FUNCTION_NAME \
  --runtime nodejs18.x \
  --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$PROJECT_NAME-$ENVIRONMENT-lambda-execution-role \
  --handler index.handler \
  --zip-file fileb://ai-chat-lambda.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{CONVERSATIONS_TABLE=$PROJECT_NAME-$ENVIRONMENT-conversations,USERS_TABLE=$PROJECT_NAME-$ENVIRONMENT-users}" \
  --region $REGION 2>/dev/null || \
aws lambda update-function-code \
  --function-name $AI_CHAT_FUNCTION_NAME \
  --zip-file fileb://ai-chat-lambda.zip \
  --region $REGION

AI_CHAT_LAMBDA_ARN=$(aws lambda get-function \
  --function-name $AI_CHAT_FUNCTION_NAME \
  --query 'Configuration.FunctionArn' \
  --output text --region $REGION)

# Package and deploy Auth Lambda
cd ../auth
zip -r auth-lambda.zip . -x "*.git*" "node_modules/*"

AUTH_FUNCTION_NAME="$PROJECT_NAME-$ENVIRONMENT-auth"
aws lambda create-function \
  --function-name $AUTH_FUNCTION_NAME \
  --runtime nodejs18.x \
  --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$PROJECT_NAME-$ENVIRONMENT-lambda-execution-role \
  --handler index.handler \
  --zip-file fileb://auth-lambda.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{USERS_TABLE=$PROJECT_NAME-$ENVIRONMENT-users}" \
  --region $REGION 2>/dev/null || \
aws lambda update-function-code \
  --function-name $AUTH_FUNCTION_NAME \
  --zip-file fileb://auth-lambda.zip \
  --region $REGION

AUTH_LAMBDA_ARN=$(aws lambda get-function \
  --function-name $AUTH_FUNCTION_NAME \
  --query 'Configuration.FunctionArn' \
  --output text --region $REGION)

echo "✅ AI Chat Lambda ARN: $AI_CHAT_LAMBDA_ARN"
echo "✅ Auth Lambda ARN: $AUTH_LAMBDA_ARN"

# Step 3: Deploy API Gateway
echo "🌐 Deploying API Gateway..."
cd ../../cloudformation
aws cloudformation deploy \
  --template-file api-gateway.yaml \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-api-gateway" \
  --parameter-overrides \
    ProjectName=$PROJECT_NAME \
    Environment=$ENVIRONMENT \
    AIChatLambdaArn=$AI_CHAT_LAMBDA_ARN \
    AuthLambdaArn=$AUTH_LAMBDA_ARN \
    UserPoolArn=$USER_POOL_ARN \
  --capabilities CAPABILITY_IAM \
  --region $REGION

API_GATEWAY_URL=$(aws cloudformation describe-stacks \
  --stack-name "$PROJECT_NAME-$ENVIRONMENT-api-gateway" \
  --query 'Stacks[0].Outputs[?OutputKey==`RestApiUrl`].OutputValue' \
  --output text --region $REGION)

echo "✅ API Gateway URL: $API_GATEWAY_URL"

# Step 4: Build the React application with real AWS config
echo "📦 Building React application with AWS configuration..."
cd ../../../frontend

# Create environment file with real AWS values
cat > .env.production << EOF
REACT_APP_USER_POOL_ID=$USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
REACT_APP_AWS_REGION=$REGION
REACT_APP_API_GATEWAY_URL=$API_GATEWAY_URL
REACT_APP_S3_BUCKET=$BUCKET_NAME
EOF

npm run build

# Step 5: Create S3 bucket if it doesn't exist
echo "🪣 Setting up S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Step 6: Configure S3 bucket for static website hosting
echo "🌐 Configuring S3 for static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Step 7: Set bucket policy for public read access
echo "🔓 Setting bucket policy..."
cat > bucket-policy.json << EOF
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
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
rm bucket-policy.json

# Step 8: Upload build files to S3
echo "⬆️ Uploading files to S3..."
aws s3 sync build/ s3://$BUCKET_NAME --delete --cache-control "max-age=31536000" --exclude "*.html"
aws s3 sync build/ s3://$BUCKET_NAME --delete --cache-control "max-age=0" --include "*.html"

# Step 9: Create CloudFront distribution (if not exists)
if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
  echo "☁️ Creating CloudFront distribution..."
  
  # Update the origin domain name in the config
  sed "s/nandhakumar-ai-assistant.s3.amazonaws.com/$BUCKET_NAME.s3.amazonaws.com/g" cloudfront-config.json > temp-config.json
  
  DISTRIBUTION_OUTPUT=$(aws cloudfront create-distribution --distribution-config file://temp-config.json)
  CLOUDFRONT_DISTRIBUTION_ID=$(echo $DISTRIBUTION_OUTPUT | jq -r '.Distribution.Id')
  CLOUDFRONT_DOMAIN=$(echo $DISTRIBUTION_OUTPUT | jq -r '.Distribution.DomainName')
  
  rm temp-config.json
  
  echo "✅ CloudFront distribution created!"
  echo "📋 Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID"
  echo "🌍 Domain: $CLOUDFRONT_DOMAIN"
  echo ""
  echo "⚠️ Please update this script with the Distribution ID for future deployments:"
  echo "CLOUDFRONT_DISTRIBUTION_ID=\"$CLOUDFRONT_DISTRIBUTION_ID\""
else
  echo "♻️ Invalidating CloudFront cache..."
  aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
  
  # Get the domain name
  CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution --id $CLOUDFRONT_DISTRIBUTION_ID | jq -r '.Distribution.DomainName')
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Your application is available at:"
echo "🌐 S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "⚡ CloudFront: https://$CLOUDFRONT_DOMAIN"
echo ""
echo "⏱️ Note: CloudFront distribution may take 15-20 minutes to fully deploy."
echo ""

# Step 10: Display deployment summary
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Your AI Assistant is now live at:"
echo "🌐 S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
if [ ! -z "$CLOUDFRONT_DOMAIN" ]; then
  echo "⚡ CloudFront: https://$CLOUDFRONT_DOMAIN"
fi
echo ""
echo "🔧 AWS Resources Created:"
echo "✅ Cognito User Pool: $USER_POOL_ID"
echo "✅ Cognito Client: $USER_POOL_CLIENT_ID"
echo "✅ API Gateway: $API_GATEWAY_URL"
echo "✅ Lambda Functions: AI Chat & Auth"
echo "✅ DynamoDB Tables: Users, Conversations, Analytics, Sessions"
echo "✅ S3 Bucket: $BUCKET_NAME"
echo "✅ CloudFront Distribution: Ready for global access"
echo ""
echo "🔐 Authentication: AWS Cognito User Pool"
echo "🤖 AI Processing: AWS Lambda + Bedrock"
echo "📊 Data Storage: DynamoDB"
echo "🌍 Global CDN: CloudFront"
echo ""
echo "⏱️ Note: CloudFront distribution may take 15-20 minutes to fully deploy."
echo ""
echo "🚀 Your production-grade AI Assistant is ready!"
echo "Users can now sign up, authenticate, and chat with the AI assistant."
echo ""
