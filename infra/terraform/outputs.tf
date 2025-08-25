# Voice Assistant AI - Terraform Outputs
# Output values for the voice assistant infrastructure

# API Gateway Outputs
output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_gateway_url
}

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = module.api_gateway.api_gateway_id
}

output "api_gateway_stage" {
  description = "API Gateway stage name"
  value       = module.api_gateway.stage_name
}

output "api_gateway_execution_arn" {
  description = "API Gateway execution ARN"
  value       = module.api_gateway.execution_arn
}

# Lambda Function Outputs
output "chatbot_lambda_arn" {
  description = "Chatbot Lambda function ARN"
  value       = module.lambda.chatbot_lambda_arn
}

output "chatbot_lambda_name" {
  description = "Chatbot Lambda function name"
  value       = module.lambda.chatbot_lambda_name
}

output "auth_lambda_arn" {
  description = "Auth Lambda function ARN"
  value       = module.lambda.auth_lambda_arn
}

output "auth_lambda_name" {
  description = "Auth Lambda function name"
  value       = module.lambda.auth_lambda_name
}

output "monitoring_lambda_arn" {
  description = "Monitoring Lambda function ARN"
  value       = module.lambda.monitoring_lambda_arn
}

output "monitoring_lambda_name" {
  description = "Monitoring Lambda function name"
  value       = module.lambda.monitoring_lambda_name
}

# DynamoDB Outputs
output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = module.dynamodb.table_name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = module.dynamodb.table_arn
}

output "dynamodb_table_stream_arn" {
  description = "DynamoDB table stream ARN"
  value       = module.dynamodb.table_stream_arn
}

# Cognito Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN"
  value       = module.cognito.user_pool_arn
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = module.cognito.user_pool_client_id
  sensitive   = true
}

output "cognito_user_pool_domain" {
  description = "Cognito User Pool Domain"
  value       = module.cognito.domain_name
}

output "cognito_identity_pool_id" {
  description = "Cognito Identity Pool ID"
  value       = module.cognito.identity_pool_id
}

# Amazon Lex Outputs
output "lex_bot_id" {
  description = "Amazon Lex Bot ID"
  value       = module.lex.bot_id
}

output "lex_bot_arn" {
  description = "Amazon Lex Bot ARN"
  value       = module.lex.bot_arn
}

# Lex bot alias outputs commented out as alias creation is manual
# output "lex_bot_alias_id" {
#   description = "Amazon Lex Bot Alias ID"
#   value       = module.lex.bot_alias_id
# }

output "lex_bot_locale" {
  description = "Amazon Lex Bot Locale"
  value       = module.lex.bot_locale_id
}

# S3 Outputs
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.s3.bucket_arn
}

output "s3_bucket_domain_name" {
  description = "S3 bucket domain name"
  value       = module.s3.bucket_domain_name
}

output "s3_bucket_regional_domain_name" {
  description = "S3 bucket regional domain name"
  value       = module.s3.bucket_regional_domain_name
}

output "s3_web_bucket_name" {
  description = "S3 web bucket name for static hosting"
  value       = module.s3.web_bucket_name
}

output "s3_web_bucket_website_endpoint" {
  description = "S3 web bucket website endpoint"
  value       = module.s3.web_bucket_website_endpoint
}

output "s3_web_bucket_website_url" {
  description = "S3 web bucket website URL"
  value       = "http://${module.s3.web_bucket_website_endpoint}"
}

# CloudWatch Outputs
output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups"
  value = {
    api_gateway = aws_cloudwatch_log_group.api_gateway.name
    lex         = aws_cloudwatch_log_group.lex.name
    lambda      = module.lambda.log_group_names
  }
}

# SNS Outputs
output "sns_alerts_topic_arn" {
  description = "SNS alerts topic ARN"
  value       = aws_sns_topic.alerts.arn
}

# Security Outputs
output "kms_key_id" {
  description = "KMS key ID for encryption"
  value       = module.lambda.kms_key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = module.lambda.kms_key_arn
}

# IAM Outputs
output "lambda_execution_role_arn" {
  description = "Lambda execution role ARN"
  value       = module.lambda.execution_role_arn
}

output "api_gateway_role_arn" {
  description = "API Gateway role ARN"
  value       = module.api_gateway.execution_role_arn
}

# Network Outputs (if VPC is used)
output "vpc_config" {
  description = "VPC configuration for Lambda functions"
  value = length(var.vpc_subnet_ids) > 0 ? {
    subnet_ids         = var.vpc_subnet_ids
    security_group_ids = var.vpc_security_group_ids
  } : null
}

# Application Configuration Outputs
output "application_config" {
  description = "Application configuration for frontend"
  value = {
    api_gateway_url        = module.api_gateway.api_gateway_url
    cognito_user_pool_id   = module.cognito.user_pool_id
    cognito_client_id      = module.cognito.user_pool_client_id
    cognito_identity_pool  = module.cognito.identity_pool_id
    cognito_domain         = module.cognito.domain_name
    s3_bucket             = module.s3.bucket_name
    aws_region            = var.aws_region
    environment           = var.environment
  }
  sensitive = true
}

# Alexa Integration Outputs
output "alexa_skill_config" {
  description = "Configuration for Alexa Skill"
  value = var.enable_alexa_integration ? {
    lambda_arn = module.lambda.chatbot_lambda_arn
    api_endpoint = "${module.api_gateway.api_gateway_url}/alexa"
  } : null
}

# Monitoring URLs
output "monitoring_urls" {
  description = "URLs for monitoring and observability"
  value = {
    cloudwatch_dashboard = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
    xray_traces         = "https://${data.aws_region.current.name}.console.aws.amazon.com/xray/home?region=${data.aws_region.current.name}#/traces"
    lambda_insights     = "https://${data.aws_region.current.name}.console.aws.amazon.com/lambda/home?region=${data.aws_region.current.name}#/functions"
  }
}

# Cost Tracking
output "cost_allocation_tags" {
  description = "Cost allocation tags for billing"
  value = var.enable_cost_allocation_tags ? {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  } : null
}

# Health Check Endpoints
output "health_check_endpoints" {
  description = "Health check endpoints for monitoring"
  value = {
    api_gateway = "${module.api_gateway.api_gateway_url}/health"
    lambda      = module.lambda.health_check_urls
  }
}

# Deployment Information
output "deployment_info" {
  description = "Deployment information"
  value = {
    terraform_version = "~> 1.0"
    aws_region       = var.aws_region
    environment      = var.environment
    project_name     = var.project_name
    deployed_at      = timestamp()
  }
}
