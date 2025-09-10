#!/bin/bash

# Setup SonarQube Secrets in AWS Secrets Manager
# This script helps you store SonarQube credentials securely in AWS

set -e

# Default values
SECRET_NAME="voice-assistant-ai/sonar-token"
REGION="us-east-1"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            SONAR_TOKEN="$2"
            shift 2
            ;;
        --secret-name)
            SECRET_NAME="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --token <sonar-token> [--secret-name <secret-name>] [--region <region>]"
            echo ""
            echo "Options:"
            echo "  --token <sonar-token>     SonarQube token (required)"
            echo "  --secret-name <name>      Secret name (default: voice-assistant-ai/sonar-token)"
            echo "  --region <region>         AWS region (default: us-east-1)"
            echo "  -h, --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Check if SonarQube token is provided
if [ -z "$SONAR_TOKEN" ]; then
    echo "❌ Error: SonarQube token is required"
    echo "Usage: $0 --token <sonar-token>"
    exit 1
fi

echo "🔐 Setting up SonarQube secrets in AWS Secrets Manager..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

# Check if AWS is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is installed and configured"

# Create or update the secret
echo "📝 Storing SonarQube token in AWS Secrets Manager..."

if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$REGION" &> /dev/null; then
    echo "🔄 Updating existing secret..."
    aws secretsmanager update-secret --secret-id "$SECRET_NAME" --secret-string "$SONAR_TOKEN" --region "$REGION"
    echo "✅ Secret updated successfully!"
else
    echo "🆕 Creating new secret..."
    aws secretsmanager create-secret --name "$SECRET_NAME" --secret-string "$SONAR_TOKEN" --region "$REGION"
    echo "✅ Secret created successfully!"
fi

echo ""
echo "🎉 SonarQube secrets setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Deploy your Terraform infrastructure: terraform apply"
echo "2. The CodePipeline will now use the stored SonarQube token"
echo "3. Monitor the pipeline execution in the AWS Console"
echo ""
echo "🔧 Useful Commands:"
echo "- View secret: aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $REGION"
echo "- Delete secret: aws secretsmanager delete-secret --secret-id $SECRET_NAME --region $REGION"
echo "- List secrets: aws secretsmanager list-secrets --region $REGION"
