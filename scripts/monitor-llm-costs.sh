#!/bin/bash

# Monitor LLM costs for Voice Assistant AI
# Track AWS Bedrock, Lambda, DynamoDB, and API Gateway costs

echo "💰 Voice Assistant AI - LLM Cost Monitor"
echo "========================================"

# Set date range (last 30 days)
START_DATE=$(date -d "30 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)

echo "📅 Cost period: $START_DATE to $END_DATE"
echo ""

# Function to get cost for a service
get_service_cost() {
    local service=$1
    local cost=$(aws ce get-cost-and-usage \
        --time-period Start=$START_DATE,End=$END_DATE \
        --granularity MONTHLY \
        --metrics BlendedCost \
        --group-by Type=DIMENSION,Key=SERVICE \
        --query "ResultsByTime[0].Groups[?Keys[0]=='$service'].Metrics.BlendedCost.Amount" \
        --output text 2>/dev/null || echo "0")
    
    if [ "$cost" = "None" ] || [ -z "$cost" ]; then
        cost="0"
    fi
    echo $cost
}

# Get costs for each service
echo "🔍 Fetching cost data..."

BEDROCK_COST=$(get_service_cost "Amazon Bedrock")
LAMBDA_COST=$(get_service_cost "AWS Lambda")
DYNAMODB_COST=$(get_service_cost "Amazon DynamoDB")
API_GATEWAY_COST=$(get_service_cost "Amazon API Gateway")
S3_COST=$(get_service_cost "Amazon Simple Storage Service")
CLOUDFRONT_COST=$(get_service_cost "Amazon CloudFront")

# Calculate total
TOTAL_COST=$(echo "$BEDROCK_COST + $LAMBDA_COST + $DYNAMODB_COST + $API_GATEWAY_COST + $S3_COST + $CLOUDFRONT_COST" | bc -l 2>/dev/null || echo "0")

echo ""
echo "💸 Cost Breakdown (Last 30 Days):"
echo "=================================="
printf "🧠 Bedrock (LLM):     $%8.2f\n" $BEDROCK_COST
printf "⚡ Lambda:            $%8.2f\n" $LAMBDA_COST
printf "🗄️  DynamoDB:          $%8.2f\n" $DYNAMODB_COST
printf "🌐 API Gateway:       $%8.2f\n" $API_GATEWAY_COST
printf "📦 S3 Storage:        $%8.2f\n" $S3_COST
printf "🚀 CloudFront:        $%8.2f\n" $CLOUDFRONT_COST
echo "=================================="
printf "💰 TOTAL:             $%8.2f\n" $TOTAL_COST

echo ""
echo "📊 Cost Analysis:"
echo "=================="

# Cost efficiency analysis
if (( $(echo "$TOTAL_COST < 5" | bc -l) )); then
    echo "✅ Excellent! Costs are very low (under $5/month)"
elif (( $(echo "$TOTAL_COST < 15" | bc -l) )); then
    echo "✅ Good! Costs are reasonable (under $15/month)"
elif (( $(echo "$TOTAL_COST < 30" | bc -l) )); then
    echo "⚠️  Moderate costs ($15-30/month) - consider optimization"
else
    echo "🚨 High costs (over $30/month) - optimization needed!"
fi

# Bedrock cost analysis
if (( $(echo "$BEDROCK_COST > 0" | bc -l) )); then
    echo "🧠 Bedrock Claude Haiku is active and cost-effective"
else
    echo "ℹ️  No Bedrock costs detected - LLM may not be in use"
fi

echo ""
echo "💡 Cost Optimization Tips:"
echo "=========================="
echo "• Claude Haiku is ~90% cheaper than GPT-4"
echo "• Conversation history limited to 8 exchanges"
echo "• Max tokens set to 300 for cost efficiency"
echo "• DynamoDB uses pay-per-request billing"
echo "• Consider setting up billing alerts"

echo ""
echo "🔗 Useful Commands:"
echo "=================="
echo "• View detailed costs: aws ce get-cost-and-usage --help"
echo "• Set billing alerts: AWS Console > Billing > Budgets"
echo "• Monitor usage: AWS Console > Cost Explorer"

echo ""
echo "✅ Cost monitoring complete!"
