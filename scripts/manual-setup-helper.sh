#!/bin/bash

# Voice Assistant AI - Manual Setup Helper Script
# This script helps automate some parts of the manual AWS setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="voice-assistant-ai"
ENVIRONMENT="prod"
AWS_REGION="us-east-1"

# Generate random suffix for unique resource names
RANDOM_SUFFIX=$(date +%s | tail -c 6)

echo -e "${BLUE}🚀 Voice Assistant AI - Manual Setup Helper${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check AWS CLI configuration
check_aws_config() {
    print_info "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS CLI is configured"
    
    # Display current AWS identity
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
    print_info "AWS Account: $ACCOUNT_ID"
    print_info "User: $USER_ARN"
}

# Create IAM roles
create_iam_roles() {
    print_info "Creating IAM roles..."
    
    # Lambda execution role
    LAMBDA_ROLE_NAME="${PROJECT_NAME}-lambda-role"
    
    # Check if role exists
    if aws iam get-role --role-name $LAMBDA_ROLE_NAME &> /dev/null; then
        print_warning "Lambda role $LAMBDA_ROLE_NAME already exists"
    else
        # Create trust policy
        cat > /tmp/lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

        aws iam create-role \
            --role-name $LAMBDA_ROLE_NAME \
            --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
            --description "Lambda execution role for Voice Assistant AI"
        
        # Attach policies
        aws iam attach-role-policy \
            --role-name $LAMBDA_ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        aws iam attach-role-policy \
            --role-name $LAMBDA_ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
        
        aws iam attach-role-policy \
            --role-name $LAMBDA_ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
        
        aws iam attach-role-policy \
            --role-name $LAMBDA_ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/AmazonLexFullAccess
        
        print_status "Created Lambda execution role: $LAMBDA_ROLE_NAME"
    fi
    
    # Get role ARN for later use
    LAMBDA_ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query Role.Arn --output text)
    echo "LAMBDA_ROLE_ARN=$LAMBDA_ROLE_ARN" >> /tmp/voice-assistant-config.env
}

# Create DynamoDB tables
create_dynamodb_tables() {
    print_info "Creating DynamoDB tables..."
    
    # Conversations table
    CONVERSATIONS_TABLE="${PROJECT_NAME}-${ENVIRONMENT}-conversations"
    
    if aws dynamodb describe-table --table-name $CONVERSATIONS_TABLE &> /dev/null; then
        print_warning "Table $CONVERSATIONS_TABLE already exists"
    else
        aws dynamodb create-table \
            --table-name $CONVERSATIONS_TABLE \
            --attribute-definitions \
                AttributeName=user_id,AttributeType=S \
                AttributeName=conversation_id,AttributeType=S \
                AttributeName=timestamp,AttributeType=N \
            --key-schema \
                AttributeName=user_id,KeyType=HASH \
                AttributeName=conversation_id,KeyType=RANGE \
            --global-secondary-indexes \
                IndexName=timestamp-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=timestamp,KeyType=RANGE}],Projection={ProjectionType=ALL} \
            --billing-mode PAY_PER_REQUEST \
            --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
        
        print_status "Created DynamoDB table: $CONVERSATIONS_TABLE"
    fi
    
    # Sessions table
    SESSIONS_TABLE="${PROJECT_NAME}-${ENVIRONMENT}-sessions"
    
    if aws dynamodb describe-table --table-name $SESSIONS_TABLE &> /dev/null; then
        print_warning "Table $SESSIONS_TABLE already exists"
    else
        aws dynamodb create-table \
            --table-name $SESSIONS_TABLE \
            --attribute-definitions AttributeName=session_id,AttributeType=S \
            --key-schema AttributeName=session_id,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST
        
        print_status "Created DynamoDB table: $SESSIONS_TABLE"
    fi
    
    echo "CONVERSATIONS_TABLE=$CONVERSATIONS_TABLE" >> /tmp/voice-assistant-config.env
    echo "SESSIONS_TABLE=$SESSIONS_TABLE" >> /tmp/voice-assistant-config.env
}

# Create S3 buckets
create_s3_buckets() {
    print_info "Creating S3 buckets..."
    
    # Files bucket
    FILES_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-files-${RANDOM_SUFFIX}"
    
    if aws s3 ls s3://$FILES_BUCKET &> /dev/null; then
        print_warning "Bucket $FILES_BUCKET already exists"
    else
        aws s3 mb s3://$FILES_BUCKET --region $AWS_REGION
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket $FILES_BUCKET \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket $FILES_BUCKET \
            --server-side-encryption-configuration '{
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }'
        
        print_status "Created S3 bucket: $FILES_BUCKET"
    fi
    
    # Web hosting bucket
    WEB_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-web-${RANDOM_SUFFIX}"
    
    if aws s3 ls s3://$WEB_BUCKET &> /dev/null; then
        print_warning "Bucket $WEB_BUCKET already exists"
    else
        aws s3 mb s3://$WEB_BUCKET --region $AWS_REGION
        
        # Configure for static website hosting
        aws s3api put-bucket-website \
            --bucket $WEB_BUCKET \
            --website-configuration '{
                "IndexDocument": {"Suffix": "index.html"},
                "ErrorDocument": {"Key": "error.html"}
            }'
        
        # Set bucket policy for public read access
        cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$WEB_BUCKET/*"
        }
    ]
}
EOF
        
        aws s3api put-bucket-policy \
            --bucket $WEB_BUCKET \
            --policy file:///tmp/bucket-policy.json
        
        print_status "Created S3 web bucket: $WEB_BUCKET"
    fi
    
    echo "FILES_BUCKET=$FILES_BUCKET" >> /tmp/voice-assistant-config.env
    echo "WEB_BUCKET=$WEB_BUCKET" >> /tmp/voice-assistant-config.env
    echo "WEB_URL=http://$WEB_BUCKET.s3-website-$AWS_REGION.amazonaws.com" >> /tmp/voice-assistant-config.env
}

# Create Cognito User Pool
create_cognito_user_pool() {
    print_info "Creating Cognito User Pool..."
    
    USER_POOL_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
    
    # Check if user pool exists
    EXISTING_POOL=$(aws cognito-idp list-user-pools --max-items 60 --query "UserPools[?Name=='$USER_POOL_NAME'].Id" --output text)
    
    if [ ! -z "$EXISTING_POOL" ]; then
        print_warning "User Pool $USER_POOL_NAME already exists"
        USER_POOL_ID=$EXISTING_POOL
    else
        USER_POOL_ID=$(aws cognito-idp create-user-pool \
            --pool-name $USER_POOL_NAME \
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
            }' \
            --query UserPool.Id --output text)
        
        print_status "Created Cognito User Pool: $USER_POOL_ID"
    fi
    
    # Create app client
    CLIENT_NAME="${PROJECT_NAME}-web-client"
    CLIENT_ID=$(aws cognito-idp create-user-pool-client \
        --user-pool-id $USER_POOL_ID \
        --client-name $CLIENT_NAME \
        --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
        --supported-identity-providers COGNITO \
        --query UserPoolClient.ClientId --output text)
    
    print_status "Created Cognito App Client: $CLIENT_ID"
    
    echo "USER_POOL_ID=$USER_POOL_ID" >> /tmp/voice-assistant-config.env
    echo "CLIENT_ID=$CLIENT_ID" >> /tmp/voice-assistant-config.env
}

# Create SNS topic for alerts
create_sns_topic() {
    print_info "Creating SNS topic for alerts..."
    
    TOPIC_NAME="${PROJECT_NAME}-${ENVIRONMENT}-alerts"
    
    TOPIC_ARN=$(aws sns create-topic --name $TOPIC_NAME --query TopicArn --output text)
    print_status "Created SNS topic: $TOPIC_ARN"
    
    echo "SNS_TOPIC_ARN=$TOPIC_ARN" >> /tmp/voice-assistant-config.env
    
    print_info "To subscribe to alerts, run:"
    print_info "aws sns subscribe --topic-arn $TOPIC_ARN --protocol email --notification-endpoint your-email@company.com"
}

# Generate configuration summary
generate_config_summary() {
    print_info "Generating configuration summary..."
    
    # Load all configuration
    source /tmp/voice-assistant-config.env
    
    cat > voice-assistant-config.txt << EOF
# Voice Assistant AI - Configuration Summary
# Generated on $(date)

## AWS Resources Created:
- Lambda Role ARN: $LAMBDA_ROLE_ARN
- DynamoDB Conversations Table: $CONVERSATIONS_TABLE
- DynamoDB Sessions Table: $SESSIONS_TABLE
- S3 Files Bucket: $FILES_BUCKET
- S3 Web Bucket: $WEB_BUCKET
- Web URL: $WEB_URL
- Cognito User Pool ID: $USER_POOL_ID
- Cognito Client ID: $CLIENT_ID
- SNS Topic ARN: $SNS_TOPIC_ARN

## Next Steps:
1. Create Lambda functions using AWS Console
2. Create API Gateway and configure endpoints
3. Create Amazon Lex bot
4. Configure frontend environment variables
5. Deploy frontend to S3 web bucket

## Frontend Environment Variables:
REACT_APP_API_GATEWAY_URL=[TO_BE_CREATED]
REACT_APP_COGNITO_USER_POOL_ID=$USER_POOL_ID
REACT_APP_COGNITO_CLIENT_ID=$CLIENT_ID
REACT_APP_S3_BUCKET=$FILES_BUCKET
REACT_APP_AWS_REGION=$AWS_REGION
REACT_APP_ENVIRONMENT=$ENVIRONMENT

## Lambda Environment Variables:
DYNAMODB_TABLE_NAME=$CONVERSATIONS_TABLE
S3_BUCKET_NAME=$FILES_BUCKET
ENVIRONMENT=$ENVIRONMENT
EOF

    print_status "Configuration saved to: voice-assistant-config.txt"
}

# Main execution
main() {
    echo -e "${BLUE}Starting automated resource creation...${NC}"
    echo ""
    
    # Initialize config file
    echo "# Voice Assistant AI Configuration" > /tmp/voice-assistant-config.env
    echo "AWS_REGION=$AWS_REGION" >> /tmp/voice-assistant-config.env
    echo "PROJECT_NAME=$PROJECT_NAME" >> /tmp/voice-assistant-config.env
    echo "ENVIRONMENT=$ENVIRONMENT" >> /tmp/voice-assistant-config.env
    
    check_aws_config
    create_iam_roles
    create_dynamodb_tables
    create_s3_buckets
    create_cognito_user_pool
    create_sns_topic
    generate_config_summary
    
    echo ""
    print_status "Automated setup completed!"
    print_info "Check 'voice-assistant-config.txt' for all resource details"
    print_info "Continue with manual steps in the README for Lambda, API Gateway, and Lex setup"
    
    # Cleanup temp files
    rm -f /tmp/lambda-trust-policy.json /tmp/bucket-policy.json /tmp/voice-assistant-config.env
}

# Run main function
main "$@"
