# Voice Assistant AI - Deployment Guide

This guide provides step-by-step instructions for deploying the Voice Assistant AI application to AWS.

## 📋 Prerequisites

### Required Tools
- **AWS CLI** (v2.0+) - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **Terraform** (v1.0+) - [Installation Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- **Node.js** (v18+) - [Installation Guide](https://nodejs.org/)
- **Python** (v3.9+) - [Installation Guide](https://www.python.org/downloads/)
- **Docker** (optional) - [Installation Guide](https://docs.docker.com/get-docker/)

### AWS Account Setup
1. **AWS Account** with appropriate permissions
2. **IAM User** with programmatic access
3. **AWS CLI** configured with credentials

### Required AWS Services
- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- Amazon Cognito
- Amazon Lex
- Amazon S3
- AWS CloudWatch
- AWS KMS
- AWS Secrets Manager

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd voice-assistant-ai

# Install dependencies
make install-deps

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### 3. Deploy Infrastructure
```bash
# Initialize Terraform
make init-terraform

# Plan deployment
make plan-infra

# Deploy infrastructure
make deploy-infra
```

### 4. Deploy Application
```bash
# Build and deploy Lambda functions
make deploy-lambda

# Deploy frontend
make deploy-frontend
```

### 5. Configure Lex Bot
```bash
# Deploy Lex bot configuration
make deploy-lex
```

## 📖 Detailed Deployment Steps

### Step 1: Environment Configuration

#### 1.1 Create Environment File
```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

#### 1.2 Configure Variables
Edit `infra/terraform/terraform.tfvars`:

```hcl
# Basic Configuration
aws_region = "us-east-1"
project_name = "voice-assistant-ai"
environment = "prod"

# Networking (optional)
vpc_subnet_ids = []
vpc_security_group_ids = []

# DynamoDB Configuration
dynamodb_billing_mode = "PAY_PER_REQUEST"

# Lambda Configuration
lambda_runtime = "python3.9"
lambda_timeout = 30
lambda_memory_size = 512
lambda_reserved_concurrency = 10

# Monitoring
log_retention_days = 14
enable_xray_tracing = true
alert_email_addresses = ["admin@yourcompany.com"]

# Security
enable_cost_allocation_tags = true
kms_key_deletion_window = 7

# Features
enable_alexa_integration = true
enable_web_interface = true
enable_voice_recording = true
enable_analytics = true
```

### Step 2: Infrastructure Deployment

#### 2.1 Initialize Terraform
```bash
cd infra/terraform
terraform init
```

#### 2.2 Plan Infrastructure
```bash
terraform plan -var-file="terraform.tfvars"
```

#### 2.3 Deploy Infrastructure
```bash
terraform apply -var-file="terraform.tfvars"
```

#### 2.4 Verify Deployment
```bash
# Check outputs
terraform output

# Verify resources in AWS Console
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `voice-assistant-ai`)]'
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `voice-assistant-ai`)]'
```

### Step 3: Lambda Function Deployment

#### 3.1 Package Lambda Functions
```bash
cd backend/lambda_functions

# Package chatbot handler
python ../../pipeline/scripts/package_lambda.py \
  --function-dir chatbot_handler \
  --environment prod \
  --publish-version \
  --update-alias prod

# Package auth handler
python ../../pipeline/scripts/package_lambda.py \
  --function-dir auth_handler \
  --environment prod \
  --publish-version \
  --update-alias prod

# Package monitoring handler
python ../../pipeline/scripts/package_lambda.py \
  --function-dir monitoring_handler \
  --environment prod \
  --publish-version \
  --update-alias prod
```

#### 3.2 Update Environment Variables
```bash
# Get infrastructure outputs
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
DYNAMODB_TABLE=$(terraform output -raw dynamodb_table_name)
S3_BUCKET=$(terraform output -raw s3_bucket_name)

# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name voice-assistant-ai-chatbot-prod \
  --environment Variables="{
    DYNAMODB_TABLE_NAME=$DYNAMODB_TABLE,
    S3_BUCKET_NAME=$S3_BUCKET,
    ENVIRONMENT=prod
  }"
```

### Step 4: Amazon Lex Bot Deployment

#### 4.1 Deploy Lex Bot
```bash
cd pipeline/scripts

# Deploy Lex bot
python deploy_lex.py \
  --bot-config ../../lex/bot-config.json \
  --locale-config ../../lex/locale-config.json \
  --intents-config ../../lex/intents.json \
  --slot-types-config ../../lex/slot-types.json \
  --environment prod \
  --lambda-arn $(aws lambda get-function --function-name voice-assistant-ai-chatbot-prod --query 'Configuration.FunctionArn' --output text)
```

#### 4.2 Test Lex Bot
```bash
# Test bot functionality
python test_lex_bot.py \
  --bot-name voice-assistant-ai-prod-bot \
  --alias-name prod \
  --test-cases ../../lex/test-cases.json
```

### Step 5: Frontend Deployment

#### 5.1 Configure Frontend Environment
```bash
cd frontend

# Create environment file
cat > .env.production << EOF
REACT_APP_API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
REACT_APP_COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
REACT_APP_COGNITO_CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)
REACT_APP_COGNITO_IDENTITY_POOL_ID=$(terraform output -raw cognito_identity_pool_id)
REACT_APP_S3_BUCKET=$(terraform output -raw s3_bucket_name)
REACT_APP_AWS_REGION=us-east-1
REACT_APP_ENVIRONMENT=prod
EOF
```

#### 5.2 Build and Deploy Frontend
```bash
# Install dependencies
npm install

# Build application
npm run build

# Deploy to S3 (if using S3 hosting)
aws s3 sync build/ s3://$(terraform output -raw s3_bucket_name) --delete

# Or deploy to Amplify
amplify publish
```

### Step 6: Post-Deployment Configuration

#### 6.1 Configure Cognito
```bash
# Create initial admin user
aws cognito-idp admin-create-user \
  --user-pool-id $(terraform output -raw cognito_user_pool_id) \
  --username admin@yourcompany.com \
  --user-attributes Name=email,Value=admin@yourcompany.com \
  --temporary-password TempPassword123! \
  --message-action SUPPRESS
```

#### 6.2 Setup Monitoring
```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name voice-assistant-ai-prod \
  --dashboard-body file://monitoring/dashboards/main-dashboard.json

# Setup SNS notifications
aws sns subscribe \
  --topic-arn $(terraform output -raw sns_alerts_topic_arn) \
  --protocol email \
  --notification-endpoint admin@yourcompany.com
```

#### 6.3 Configure Secrets
```bash
# Store API keys and secrets
aws secretsmanager create-secret \
  --name voice-assistant-ai/api-keys \
  --description "API keys for Voice Assistant AI" \
  --secret-string '{"jwt_secret":"your-jwt-secret","encryption_key":"your-encryption-key"}'
```

## 🔧 Environment-Specific Deployments

### Development Environment
```bash
# Deploy to dev environment
terraform apply -var="environment=dev" -var-file="terraform.tfvars"

# Deploy Lambda functions
python package_lambda.py --environment dev

# Deploy frontend
REACT_APP_ENVIRONMENT=dev npm run build
```

### Staging Environment
```bash
# Deploy to staging environment
terraform apply -var="environment=staging" -var-file="terraform.tfvars"

# Deploy Lambda functions
python package_lambda.py --environment staging

# Deploy frontend
REACT_APP_ENVIRONMENT=staging npm run build
```

### Production Environment
```bash
# Deploy to production environment
terraform apply -var="environment=prod" -var-file="terraform.tfvars"

# Deploy Lambda functions with versioning
python package_lambda.py --environment prod --publish-version --update-alias prod

# Deploy frontend with optimizations
REACT_APP_ENVIRONMENT=prod npm run build
```

## 🔍 Verification and Testing

### 1. Health Checks
```bash
# Check API Gateway health
curl https://$(terraform output -raw api_gateway_url)/health

# Check Lambda functions
aws lambda invoke --function-name voice-assistant-ai-monitoring-prod response.json
cat response.json
```

### 2. Integration Tests
```bash
# Run integration tests
cd tests
python -m pytest integration/ -v

# Test voice functionality
python test_voice_integration.py
```

### 3. Load Testing
```bash
# Run load tests
cd tests/load
artillery run load-test.yml
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Terraform State Lock
```bash
# If Terraform state is locked
terraform force-unlock <LOCK_ID>
```

#### 2. Lambda Function Timeout
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name voice-assistant-ai-chatbot-prod \
  --timeout 60
```

#### 3. DynamoDB Throttling
```bash
# Check metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ThrottledRequests \
  --dimensions Name=TableName,Value=voice-assistant-ai-prod-conversations \
  --start-time 2023-01-01T00:00:00Z \
  --end-time 2023-01-01T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

#### 4. Cognito Configuration Issues
```bash
# Verify Cognito configuration
aws cognito-idp describe-user-pool \
  --user-pool-id $(terraform output -raw cognito_user_pool_id)
```

### Logs and Monitoring
```bash
# View Lambda logs
aws logs tail /aws/lambda/voice-assistant-ai-chatbot-prod --follow

# View API Gateway logs
aws logs tail /aws/apigateway/voice-assistant-ai-prod --follow

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=voice-assistant-ai-chatbot-prod \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Sum
```

## 🔄 Updates and Maintenance

### Rolling Updates
```bash
# Update Lambda function code
python package_lambda.py --environment prod --publish-version

# Update alias to new version
aws lambda update-alias \
  --function-name voice-assistant-ai-chatbot-prod \
  --name prod \
  --function-version $NEW_VERSION
```

### Rollback Procedures
```bash
# Rollback Lambda function
aws lambda update-alias \
  --function-name voice-assistant-ai-chatbot-prod \
  --name prod \
  --function-version $PREVIOUS_VERSION

# Rollback infrastructure
terraform apply -var-file="terraform.tfvars" -target=module.lambda
```

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review CloudWatch logs
3. Consult the [Architecture Guide](ARCHITECTURE.md)
4. Contact the development team

## 🔗 Related Documentation
- [Architecture Guide](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Security Guide](SECURITY.md)
- [Monitoring Guide](MONITORING.md)
