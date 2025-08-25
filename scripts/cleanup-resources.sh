#!/bin/bash

# Voice Assistant AI - Resource Cleanup Script
# This script helps clean up AWS resources created manually or via Terraform

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

echo -e "${RED}🧹 Voice Assistant AI - Resource Cleanup${NC}"
echo -e "${RED}=======================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will delete AWS resources and may incur costs!${NC}"
echo -e "${YELLOW}⚠️  Make sure you want to proceed before continuing.${NC}"
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

# Confirmation prompt
confirm_cleanup() {
    echo -e "${YELLOW}This script will attempt to delete the following resources:${NC}"
    echo "- Lambda functions"
    echo "- API Gateway APIs"
    echo "- DynamoDB tables"
    echo "- S3 buckets (and all contents)"
    echo "- Cognito User Pools"
    echo "- IAM roles and policies"
    echo "- CloudWatch log groups"
    echo "- SNS topics"
    echo "- Lex bots"
    echo ""
    
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        print_info "Cleanup cancelled."
        exit 0
    fi
}

# Check if using Terraform
check_terraform() {
    if [ -f "infra/terraform/terraform.tfstate" ] || [ -f "infra/terraform/.terraform/terraform.tfstate" ]; then
        print_warning "Terraform state detected!"
        print_info "For Terraform-managed resources, use: cd infra/terraform && terraform destroy"
        
        read -p "Do you want to run terraform destroy? (y/n): " terraform_destroy
        
        if [ "$terraform_destroy" = "y" ] || [ "$terraform_destroy" = "Y" ]; then
            cd infra/terraform
            terraform destroy -auto-approve
            cd ../..
            print_status "Terraform resources destroyed"
            exit 0
        else
            print_info "Continuing with manual cleanup..."
        fi
    fi
}

# Delete Lambda functions
cleanup_lambda_functions() {
    print_info "Cleaning up Lambda functions..."
    
    # List and delete Lambda functions
    FUNCTIONS=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, '${PROJECT_NAME}')].FunctionName" --output text)
    
    if [ ! -z "$FUNCTIONS" ]; then
        for function in $FUNCTIONS; do
            print_info "Deleting Lambda function: $function"
            aws lambda delete-function --function-name $function || print_warning "Failed to delete $function"
        done
        print_status "Lambda functions cleanup completed"
    else
        print_info "No Lambda functions found to delete"
    fi
}

# Delete API Gateway APIs
cleanup_api_gateway() {
    print_info "Cleaning up API Gateway APIs..."
    
    # List and delete REST APIs
    APIS=$(aws apigateway get-rest-apis --query "items[?starts_with(name, '${PROJECT_NAME}')].id" --output text)
    
    if [ ! -z "$APIS" ]; then
        for api in $APIS; do
            print_info "Deleting API Gateway: $api"
            aws apigateway delete-rest-api --rest-api-id $api || print_warning "Failed to delete API $api"
        done
        print_status "API Gateway cleanup completed"
    else
        print_info "No API Gateway APIs found to delete"
    fi
}

# Delete DynamoDB tables
cleanup_dynamodb_tables() {
    print_info "Cleaning up DynamoDB tables..."
    
    # List and delete tables
    TABLES=$(aws dynamodb list-tables --query "TableNames[?starts_with(@, '${PROJECT_NAME}')]" --output text)
    
    if [ ! -z "$TABLES" ]; then
        for table in $TABLES; do
            print_info "Deleting DynamoDB table: $table"
            aws dynamodb delete-table --table-name $table || print_warning "Failed to delete table $table"
        done
        print_status "DynamoDB tables cleanup completed"
    else
        print_info "No DynamoDB tables found to delete"
    fi
}

# Delete S3 buckets
cleanup_s3_buckets() {
    print_info "Cleaning up S3 buckets..."
    
    # List buckets
    BUCKETS=$(aws s3 ls | grep $PROJECT_NAME | awk '{print $3}')
    
    if [ ! -z "$BUCKETS" ]; then
        for bucket in $BUCKETS; do
            print_info "Deleting S3 bucket: $bucket"
            
            # Delete all objects and versions
            aws s3 rm s3://$bucket --recursive || print_warning "Failed to empty bucket $bucket"
            
            # Delete all object versions (if versioning is enabled)
            aws s3api delete-objects --bucket $bucket --delete "$(aws s3api list-object-versions --bucket $bucket --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}')" 2>/dev/null || true
            
            # Delete all delete markers
            aws s3api delete-objects --bucket $bucket --delete "$(aws s3api list-object-versions --bucket $bucket --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}')" 2>/dev/null || true
            
            # Delete bucket
            aws s3 rb s3://$bucket || print_warning "Failed to delete bucket $bucket"
        done
        print_status "S3 buckets cleanup completed"
    else
        print_info "No S3 buckets found to delete"
    fi
}

# Delete Cognito User Pools
cleanup_cognito() {
    print_info "Cleaning up Cognito User Pools..."
    
    # List and delete user pools
    USER_POOLS=$(aws cognito-idp list-user-pools --max-items 60 --query "UserPools[?starts_with(Name, '${PROJECT_NAME}')].Id" --output text)
    
    if [ ! -z "$USER_POOLS" ]; then
        for pool in $USER_POOLS; do
            print_info "Deleting Cognito User Pool: $pool"
            aws cognito-idp delete-user-pool --user-pool-id $pool || print_warning "Failed to delete user pool $pool"
        done
        print_status "Cognito User Pools cleanup completed"
    else
        print_info "No Cognito User Pools found to delete"
    fi
    
    # List and delete identity pools
    IDENTITY_POOLS=$(aws cognito-identity list-identity-pools --max-results 60 --query "IdentityPools[?starts_with(IdentityPoolName, '${PROJECT_NAME}')].IdentityPoolId" --output text)
    
    if [ ! -z "$IDENTITY_POOLS" ]; then
        for pool in $IDENTITY_POOLS; do
            print_info "Deleting Cognito Identity Pool: $pool"
            aws cognito-identity delete-identity-pool --identity-pool-id $pool || print_warning "Failed to delete identity pool $pool"
        done
        print_status "Cognito Identity Pools cleanup completed"
    else
        print_info "No Cognito Identity Pools found to delete"
    fi
}

# Delete IAM roles
cleanup_iam_roles() {
    print_info "Cleaning up IAM roles..."
    
    # List and delete roles
    ROLES=$(aws iam list-roles --query "Roles[?starts_with(RoleName, '${PROJECT_NAME}')].RoleName" --output text)
    
    if [ ! -z "$ROLES" ]; then
        for role in $ROLES; do
            print_info "Deleting IAM role: $role"
            
            # Detach all policies
            ATTACHED_POLICIES=$(aws iam list-attached-role-policies --role-name $role --query 'AttachedPolicies[].PolicyArn' --output text)
            for policy in $ATTACHED_POLICIES; do
                aws iam detach-role-policy --role-name $role --policy-arn $policy || true
            done
            
            # Delete inline policies
            INLINE_POLICIES=$(aws iam list-role-policies --role-name $role --query 'PolicyNames' --output text)
            for policy in $INLINE_POLICIES; do
                aws iam delete-role-policy --role-name $role --policy-name $policy || true
            done
            
            # Delete role
            aws iam delete-role --role-name $role || print_warning "Failed to delete role $role"
        done
        print_status "IAM roles cleanup completed"
    else
        print_info "No IAM roles found to delete"
    fi
}

# Delete CloudWatch log groups
cleanup_cloudwatch_logs() {
    print_info "Cleaning up CloudWatch log groups..."
    
    # List and delete log groups
    LOG_GROUPS=$(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/${PROJECT_NAME}" --query 'logGroups[].logGroupName' --output text)
    
    if [ ! -z "$LOG_GROUPS" ]; then
        for log_group in $LOG_GROUPS; do
            print_info "Deleting CloudWatch log group: $log_group"
            aws logs delete-log-group --log-group-name $log_group || print_warning "Failed to delete log group $log_group"
        done
        print_status "CloudWatch log groups cleanup completed"
    else
        print_info "No CloudWatch log groups found to delete"
    fi
}

# Delete SNS topics
cleanup_sns_topics() {
    print_info "Cleaning up SNS topics..."
    
    # List and delete topics
    TOPICS=$(aws sns list-topics --query "Topics[?contains(TopicArn, '${PROJECT_NAME}')].TopicArn" --output text)
    
    if [ ! -z "$TOPICS" ]; then
        for topic in $TOPICS; do
            print_info "Deleting SNS topic: $topic"
            aws sns delete-topic --topic-arn $topic || print_warning "Failed to delete topic $topic"
        done
        print_status "SNS topics cleanup completed"
    else
        print_info "No SNS topics found to delete"
    fi
}

# Delete Lex bots
cleanup_lex_bots() {
    print_info "Cleaning up Lex bots..."
    
    # List and delete Lex V2 bots
    BOTS=$(aws lexv2-models list-bots --query "botSummaries[?starts_with(botName, '${PROJECT_NAME}')].botId" --output text)
    
    if [ ! -z "$BOTS" ]; then
        for bot in $BOTS; do
            print_info "Deleting Lex bot: $bot"
            aws lexv2-models delete-bot --bot-id $bot --skip-resource-in-use-check || print_warning "Failed to delete bot $bot"
        done
        print_status "Lex bots cleanup completed"
    else
        print_info "No Lex bots found to delete"
    fi
}

# Delete CloudWatch dashboards
cleanup_cloudwatch_dashboards() {
    print_info "Cleaning up CloudWatch dashboards..."
    
    # List and delete dashboards
    DASHBOARDS=$(aws cloudwatch list-dashboards --query "DashboardEntries[?starts_with(DashboardName, '${PROJECT_NAME}')].DashboardName" --output text)
    
    if [ ! -z "$DASHBOARDS" ]; then
        for dashboard in $DASHBOARDS; do
            print_info "Deleting CloudWatch dashboard: $dashboard"
            aws cloudwatch delete-dashboards --dashboard-names $dashboard || print_warning "Failed to delete dashboard $dashboard"
        done
        print_status "CloudWatch dashboards cleanup completed"
    else
        print_info "No CloudWatch dashboards found to delete"
    fi
}

# Main cleanup function
main() {
    confirm_cleanup
    check_terraform
    
    print_info "Starting resource cleanup..."
    echo ""
    
    cleanup_lambda_functions
    cleanup_api_gateway
    cleanup_lex_bots
    cleanup_dynamodb_tables
    cleanup_s3_buckets
    cleanup_cognito
    cleanup_iam_roles
    cleanup_cloudwatch_logs
    cleanup_cloudwatch_dashboards
    cleanup_sns_topics
    
    echo ""
    print_status "Cleanup completed!"
    print_warning "Please verify in AWS Console that all resources have been deleted"
    print_info "Some resources may take a few minutes to be fully deleted"
    
    # Final verification
    echo ""
    print_info "Remaining resources check:"
    
    REMAINING_FUNCTIONS=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, '${PROJECT_NAME}')].FunctionName" --output text)
    REMAINING_TABLES=$(aws dynamodb list-tables --query "TableNames[?starts_with(@, '${PROJECT_NAME}')]" --output text)
    REMAINING_BUCKETS=$(aws s3 ls | grep $PROJECT_NAME | awk '{print $3}')
    
    if [ -z "$REMAINING_FUNCTIONS" ] && [ -z "$REMAINING_TABLES" ] && [ -z "$REMAINING_BUCKETS" ]; then
        print_status "All major resources have been cleaned up successfully!"
    else
        print_warning "Some resources may still exist. Please check AWS Console."
        [ ! -z "$REMAINING_FUNCTIONS" ] && print_warning "Remaining Lambda functions: $REMAINING_FUNCTIONS"
        [ ! -z "$REMAINING_TABLES" ] && print_warning "Remaining DynamoDB tables: $REMAINING_TABLES"
        [ ! -z "$REMAINING_BUCKETS" ] && print_warning "Remaining S3 buckets: $REMAINING_BUCKETS"
    fi
}

# Run main function
main "$@"
