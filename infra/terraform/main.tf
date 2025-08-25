# Voice Assistant AI - Main Terraform Configuration
# Production-ready infrastructure for Alexa-integrated voice assistant

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DevOps"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random suffix for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# API Gateway Module
module "api_gateway" {
  source = "./modules/api-gateway"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # Lambda function ARNs (will be created by lambda module)
  chatbot_lambda_arn    = module.lambda.chatbot_lambda_arn
  auth_lambda_arn       = module.lambda.auth_lambda_arn
  monitoring_lambda_arn = module.lambda.monitoring_lambda_arn
  
  # Cognito configuration
  cognito_user_pool_arn = module.cognito.user_pool_arn
  
  tags = local.common_tags
}

# Lambda Functions Module
module "lambda" {
  source = "./modules/lambda"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # DynamoDB table name
  dynamodb_table_name = module.dynamodb.table_name
  
  # S3 bucket name
  s3_bucket_name = module.s3.bucket_name
  
  # Lex bot configuration
  lex_bot_id = module.lex.bot_id
  
  # VPC configuration (if needed)
  vpc_subnet_ids         = var.vpc_subnet_ids
  vpc_security_group_ids = var.vpc_security_group_ids
  
  tags = local.common_tags
}

# DynamoDB Module
module "dynamodb" {
  source = "./modules/dynamodb"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # Table configuration
  billing_mode = var.dynamodb_billing_mode
  
  tags = local.common_tags
}

# Cognito Module
module "cognito" {
  source = "./modules/cognito"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # Domain configuration
  domain_name = "${local.name_prefix}-auth-${random_string.suffix.result}"
  
  # Lambda triggers
  pre_authentication_lambda_arn = module.lambda.auth_lambda_arn
  
  tags = local.common_tags
}

# Amazon Lex Module
module "lex" {
  source = "./modules/lex"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # Lambda function for fulfillment
  fulfillment_lambda_arn = module.lambda.chatbot_lambda_arn
  
  # Bot configuration
  bot_locale = var.lex_bot_locale
  
  tags = local.common_tags
}

# S3 Module
module "s3" {
  source = "./modules/s3"

  name_prefix = local.name_prefix
  environment = var.environment
  
  # Bucket configuration
  bucket_suffix = random_string.suffix.result
  
  # CORS configuration for web access
  cors_allowed_origins = var.cors_allowed_origins
  
  tags = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name_prefix}"
  retention_in_days = var.log_retention_days
  
  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "lex" {
  name              = "/aws/lex/${local.name_prefix}"
  retention_in_days = var.log_retention_days
  
  tags = local.common_tags
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", "${local.name_prefix}-chatbot"],
            [".", "Errors", ".", "."],
            [".", "Invocations", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Lambda Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", "${local.name_prefix}-api"],
            [".", "Latency", ".", "."],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "API Gateway Metrics"
          period  = 300
        }
      }
    ]
  })
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"
  
  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count = length(var.alert_email_addresses)
  
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_addresses[count.index]
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = "${local.name_prefix}-chatbot"
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx" {
  alarm_name          = "${local.name_prefix}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors API Gateway 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ApiName = "${local.name_prefix}-api"
  }

  tags = local.common_tags
}
