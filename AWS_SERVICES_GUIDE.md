# 🏗️ AWS Services Configuration Guide

This guide provides detailed configuration instructions for each AWS service used in the Voice Assistant AI project.

## 📋 AWS Services Overview

| Service | Purpose | Configuration Required |
|---------|---------|----------------------|
| **Lambda** | Serverless compute | Function code, environment variables |
| **API Gateway** | REST API endpoints | Routes, CORS, authentication |
| **DynamoDB** | NoSQL database | Tables, indexes, capacity |
| **Cognito** | User authentication | User pools, identity pools |
| **Lex** | Natural language processing | Bot, intents, utterances |
| **S3** | File storage | Buckets, permissions, lifecycle |
| **CloudWatch** | Monitoring & logging | Dashboards, alarms, log groups |
| **KMS** | Encryption keys | Key policies, grants |
| **Secrets Manager** | Secure configuration | Secrets, rotation policies |

## 🔧 Service-by-Service Configuration

### 1. AWS Lambda Configuration

#### Function Settings
```bash
# Chatbot Handler Configuration
aws lambda update-function-configuration \
  --function-name voice-assistant-ai-chatbot-prod \
  --runtime python3.9 \
  --handler handler.lambda_handler \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables='{
    "DYNAMODB_TABLE_NAME":"voice-assistant-ai-prod-conversations",
    "S3_BUCKET_NAME":"voice-assistant-ai-prod-files",
    "LEX_BOT_ID":"your-lex-bot-id",
    "ENVIRONMENT":"prod",
    "LOG_LEVEL":"INFO"
  }'

# Enable X-Ray tracing
aws lambda update-function-configuration \
  --function-name voice-assistant-ai-chatbot-prod \
  --tracing-config Mode=Active

# Set reserved concurrency
aws lambda put-reserved-concurrency \
  --function-name voice-assistant-ai-chatbot-prod \
  --reserved-concurrent-executions 10
```

#### Lambda Layers (Optional)
```bash
# Create shared layer for common dependencies
zip -r shared-layer.zip python/
aws lambda publish-layer-version \
  --layer-name voice-assistant-shared \
  --description "Shared dependencies for Voice Assistant AI" \
  --zip-file fileb://shared-layer.zip \
  --compatible-runtimes python3.9

# Attach layer to function
aws lambda update-function-configuration \
  --function-name voice-assistant-ai-chatbot-prod \
  --layers arn:aws:lambda:us-east-1:123456789012:layer:voice-assistant-shared:1
```

### 2. Amazon API Gateway Configuration

#### REST API Setup
```bash
# Create REST API
aws apigateway create-rest-api \
  --name voice-assistant-ai-prod-api \
  --description "Voice Assistant AI REST API" \
  --endpoint-configuration types=REGIONAL

# Get API ID
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`voice-assistant-ai-prod-api`].id' --output text)

# Create resources and methods
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text) \
  --path-part chatbot

# Configure CORS
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

#### API Gateway Logging
```bash
# Enable CloudWatch logging
aws apigateway update-stage \
  --rest-api-id $API_ID \
  --stage-name prod \
  --patch-ops op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:us-east-1:123456789012:log-group:API-Gateway-Execution-Logs_${API_ID}/prod \
  --patch-ops op=replace,path=/accessLogSettings/format,value='$requestId $ip $caller $user [$requestTime] "$httpMethod $resourcePath $protocol" $status $error.message $error.messageString'
```

### 3. Amazon DynamoDB Configuration

#### Table Creation and Configuration
```bash
# Create conversations table
aws dynamodb create-table \
  --table-name voice-assistant-ai-prod-conversations \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=conversation_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=conversation_id,KeyType=RANGE \
  --global-secondary-indexes \
    IndexName=timestamp-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=timestamp,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name voice-assistant-ai-prod-conversations \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Configure auto-scaling (if using provisioned capacity)
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id table/voice-assistant-ai-prod-conversations \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --min-capacity 5 \
  --max-capacity 100

aws application-autoscaling put-scaling-policy \
  --service-namespace dynamodb \
  --resource-id table/voice-assistant-ai-prod-conversations \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --policy-name voice-assistant-read-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    TargetValue=70.0,PredefinedMetricSpecification='{PredefinedMetricType=DynamoDBReadCapacityUtilization}'
```

#### DynamoDB Encryption
```bash
# Enable encryption at rest
aws dynamodb update-table \
  --table-name voice-assistant-ai-prod-conversations \
  --sse-specification Enabled=true,SSEType=KMS,KMSMasterKeyId=alias/voice-assistant-ai-key
```

### 4. Amazon Cognito Configuration

#### User Pool Setup
```bash
# Create user pool
aws cognito-idp create-user-pool \
  --pool-name voice-assistant-ai-prod \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": false
    }
  }' \
  --auto-verified-attributes email \
  --username-attributes email \
  --verification-message-template '{
    "DefaultEmailOption": "CONFIRM_WITH_CODE",
    "DefaultEmailSubject": "Voice Assistant AI - Verify your email",
    "DefaultEmailMessage": "Your verification code is {####}"
  }'

# Create user pool client
aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name voice-assistant-ai-web-client \
  --generate-secret \
  --explicit-auth-flows ADMIN_NO_SRP_AUTH USER_PASSWORD_AUTH \
  --supported-identity-providers COGNITO \
  --callback-urls https://your-domain.com/callback \
  --logout-urls https://your-domain.com/logout \
  --allowed-o-auth-flows code implicit \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client
```

#### Identity Pool Setup
```bash
# Create identity pool
aws cognito-identity create-identity-pool \
  --identity-pool-name voice-assistant-ai-prod \
  --allow-unauthenticated-identities \
  --cognito-identity-providers \
    ProviderName=cognito-idp.us-east-1.amazonaws.com/$USER_POOL_ID,ClientId=$CLIENT_ID,ServerSideTokenCheck=false

# Set identity pool roles
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id $IDENTITY_POOL_ID \
  --roles authenticated=arn:aws:iam::123456789012:role/Cognito_voice_assistant_ai_prodAuth_Role,unauthenticated=arn:aws:iam::123456789012:role/Cognito_voice_assistant_ai_prodUnauth_Role
```

### 5. Amazon Lex Configuration

#### Bot Creation
```bash
# Create Lex bot
aws lexv2-models create-bot \
  --bot-name voice-assistant-ai-prod-bot \
  --description "Voice Assistant AI Bot for Production" \
  --role-arn arn:aws:iam::123456789012:role/aws-service-role/lexv2.amazonaws.com/AWSServiceRoleForLexV2Bots_ABCDEFGHIJ \
  --data-privacy '{"ChildDirected": false}' \
  --idle-session-ttl-in-seconds 300

# Create bot locale
aws lexv2-models create-bot-locale \
  --bot-id $BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --description "English (US) locale" \
  --nlu-intent-confidence-threshold 0.40 \
  --voice-settings '{"VoiceId": "Joanna", "Engine": "neural"}'

# Create intents
aws lexv2-models create-intent \
  --bot-id $BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-name WelcomeIntent \
  --description "Welcome greeting intent" \
  --sample-utterances '[
    {"Utterance": "Hello"},
    {"Utterance": "Hi"},
    {"Utterance": "Hey there"},
    {"Utterance": "Good morning"}
  ]'

# Build bot locale
aws lexv2-models build-bot-locale \
  --bot-id $BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US

# Create bot version
aws lexv2-models create-bot-version \
  --bot-id $BOT_ID \
  --description "Production version" \
  --bot-version-locale-specification '{
    "en_US": {"sourceBotVersion": "DRAFT"}
  }'

# Create bot alias
aws lexv2-models create-bot-alias \
  --bot-id $BOT_ID \
  --bot-alias-name prod \
  --description "Production alias" \
  --bot-version $BOT_VERSION
```

### 6. Amazon S3 Configuration

#### Bucket Setup
```bash
# Create S3 bucket
aws s3 mb s3://voice-assistant-ai-prod-files --region us-east-1

# Configure bucket versioning
aws s3api put-bucket-versioning \
  --bucket voice-assistant-ai-prod-files \
  --versioning-configuration Status=Enabled

# Configure bucket encryption
aws s3api put-bucket-encryption \
  --bucket voice-assistant-ai-prod-files \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/voice-assistant-ai-key"
      }
    }]
  }'

# Configure bucket lifecycle
aws s3api put-bucket-lifecycle-configuration \
  --bucket voice-assistant-ai-prod-files \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "audio-files-lifecycle",
      "Status": "Enabled",
      "Filter": {"Prefix": "audio/"},
      "Transitions": [{
        "Days": 30,
        "StorageClass": "STANDARD_IA"
      }, {
        "Days": 90,
        "StorageClass": "GLACIER"
      }]
    }]
  }'

# Configure CORS for web uploads
aws s3api put-bucket-cors \
  --bucket voice-assistant-ai-prod-files \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedOrigins": ["https://your-domain.com"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }]
  }'
```

### 7. CloudWatch Configuration

#### Log Groups
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/lambda/voice-assistant-ai-chatbot-prod
aws logs create-log-group --log-group-name /aws/lambda/voice-assistant-ai-auth-prod
aws logs create-log-group --log-group-name /aws/lambda/voice-assistant-ai-monitoring-prod
aws logs create-log-group --log-group-name /aws/apigateway/voice-assistant-ai-prod

# Set retention policy
aws logs put-retention-policy \
  --log-group-name /aws/lambda/voice-assistant-ai-chatbot-prod \
  --retention-in-days 14
```

#### Custom Metrics and Alarms
```bash
# Create custom metric alarm
aws cloudwatch put-metric-alarm \
  --alarm-name voice-assistant-ai-high-error-rate \
  --alarm-description "High error rate in chatbot function" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:voice-assistant-ai-alerts \
  --dimensions Name=FunctionName,Value=voice-assistant-ai-chatbot-prod
```

### 8. AWS KMS Configuration

#### Key Creation and Policies
```bash
# Create KMS key
aws kms create-key \
  --description "Voice Assistant AI encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT

# Create alias
aws kms create-alias \
  --alias-name alias/voice-assistant-ai-key \
  --target-key-id $KEY_ID

# Set key policy
aws kms put-key-policy \
  --key-id $KEY_ID \
  --policy-name default \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
      "Action": "kms:*",
      "Resource": "*"
    }, {
      "Sid": "Allow Lambda access",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/voice-assistant-ai-lambda-role"},
      "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*"
    }]
  }'
```

### 9. AWS Secrets Manager Configuration

#### Secrets Creation
```bash
# Create JWT secret
aws secretsmanager create-secret \
  --name voice-assistant-ai/jwt-secret \
  --description "JWT signing secret for Voice Assistant AI" \
  --secret-string "$(openssl rand -base64 32)"

# Create database credentials
aws secretsmanager create-secret \
  --name voice-assistant-ai/database \
  --description "Database credentials" \
  --secret-string '{
    "username": "admin",
    "password": "'$(openssl rand -base64 16)'"
  }'

# Configure automatic rotation
aws secretsmanager update-secret \
  --secret-id voice-assistant-ai/database \
  --description "Database credentials with rotation" \
  --kms-key-id alias/voice-assistant-ai-key
```

## 🔍 Verification Commands

### Check All Services
```bash
# Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `voice-assistant-ai`)].[FunctionName,Runtime,LastModified]' --output table

# DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `voice-assistant-ai`)]' --output table

# S3 buckets
aws s3 ls | grep voice-assistant-ai

# Cognito user pools
aws cognito-idp list-user-pools --max-items 10 --query 'UserPools[?starts_with(Name, `voice-assistant-ai`)]'

# Lex bots
aws lexv2-models list-bots --query 'botSummaries[?starts_with(botName, `voice-assistant-ai`)]'

# CloudWatch log groups
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/voice-assistant-ai

# KMS keys
aws kms list-aliases --query 'Aliases[?starts_with(AliasName, `alias/voice-assistant-ai`)]'

# Secrets
aws secretsmanager list-secrets --query 'SecretList[?starts_with(Name, `voice-assistant-ai`)]'
```

This guide provides the detailed AWS service configurations needed for the Voice Assistant AI project. Each service is configured with production-ready settings including security, monitoring, and scalability considerations.
