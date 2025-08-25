#!/bin/bash

# Deploy LLM-powered Voice Assistant with AWS Bedrock Claude Haiku
# Most cost-effective LLM solution: ~90% cheaper than OpenAI

echo "🧠 Deploying LLM-powered Voice Assistant with AWS Bedrock Claude Haiku"
echo "💰 Cost: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens"

# Set variables
REGION="us-east-1"
PROJECT_NAME="voice-assistant-ai"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Check if Bedrock Claude Haiku is available in region
echo "🔍 Checking Bedrock model availability..."
if aws bedrock list-foundation-models --region $REGION --query 'modelSummaries[?modelId==`anthropic.claude-3-haiku-20240307-v1:0`]' --output text | grep -q "anthropic.claude-3-haiku"; then
    echo "✅ Claude Haiku model available in $REGION"
else
    echo "❌ Claude Haiku model not available in $REGION. Please check Bedrock console."
    exit 1
fi

# Navigate to terraform directory
cd "$(dirname "$0")/../infra/terraform" || exit 1

# Initialize Terraform
echo "🏗️ Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning LLM infrastructure deployment..."
terraform plan -var="aws_region=$REGION"

# Ask for confirmation
read -p "🚀 Deploy LLM infrastructure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Apply Terraform
echo "🚀 Deploying LLM infrastructure..."
terraform apply -auto-approve -var="aws_region=$REGION"

# Get outputs
API_URL=$(terraform output -raw llm_api_gateway_url 2>/dev/null || echo "Not available")
CONVERSATION_TABLE=$(terraform output -raw conversation_table_name 2>/dev/null || echo "Not available")

echo ""
echo "🎉 LLM Voice Assistant Deployed Successfully!"
echo ""
echo "📊 Infrastructure Details:"
echo "  • Model: Claude Haiku (most cost-effective)"
echo "  • API Gateway: $API_URL"
echo "  • Conversation Table: $CONVERSATION_TABLE"
echo "  • Region: $REGION"
echo ""
echo "💰 Cost Optimization Features:"
echo "  • Claude Haiku: ~90% cheaper than GPT-4"
echo "  • Conversation history limited to 8 exchanges"
echo "  • Max tokens: 300 (optimized for cost)"
echo "  • DynamoDB Pay-per-request billing"
echo ""
echo "🎯 Expected Monthly Costs (light usage):"
echo "  • Bedrock Claude Haiku: $0.50-2.00"
echo "  • Lambda: $0.20-1.00"
echo "  • DynamoDB: $0.25-1.00"
echo "  • API Gateway: $0.10-0.50"
echo "  • Total: ~$1-5/month"
echo ""
echo "🔗 Next Steps:"
echo "  1. Update frontend to use new API endpoint"
echo "  2. Test LLM conversations"
echo "  3. Monitor costs in AWS Cost Explorer"
echo ""
echo "✅ LLM deployment complete!"
