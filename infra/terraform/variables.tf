# Voice Assistant AI - Terraform Variables
# Configuration variables for the voice assistant infrastructure

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-southeast-1", "ap-southeast-2", "ap-northeast-1"
    ], var.aws_region)
    error_message = "AWS region must be a valid region where all services are available."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "voice-assistant-ai"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# Lambda Configuration
variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
  
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
  
  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory size must be between 128 and 10240 MB."
  }
}

variable "lambda_reserved_concurrency" {
  description = "Reserved concurrency for Lambda functions"
  type        = number
  default     = 10
  
  validation {
    condition     = var.lambda_reserved_concurrency >= 0
    error_message = "Reserved concurrency must be a non-negative number."
  }
}

# DynamoDB Configuration
variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PAY_PER_REQUEST or PROVISIONED)"
  type        = string
  default     = "PAY_PER_REQUEST"
  
  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.dynamodb_billing_mode)
    error_message = "DynamoDB billing mode must be either PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units (only for PROVISIONED billing)"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units (only for PROVISIONED billing)"
  type        = number
  default     = 5
}

# Amazon Lex Configuration
variable "lex_bot_locale" {
  description = "Amazon Lex bot locale"
  type        = string
  default     = "en_US"
  
  validation {
    condition = contains([
      "en_US", "en_GB", "en_AU", "en_IN",
      "es_ES", "es_US", "fr_FR", "fr_CA",
      "de_DE", "it_IT", "ja_JP", "ko_KR"
    ], var.lex_bot_locale)
    error_message = "Lex bot locale must be a supported locale."
  }
}

variable "lex_bot_idle_timeout" {
  description = "Lex bot idle session timeout in seconds"
  type        = number
  default     = 300
  
  validation {
    condition     = var.lex_bot_idle_timeout >= 60 && var.lex_bot_idle_timeout <= 86400
    error_message = "Lex bot idle timeout must be between 60 and 86400 seconds."
  }
}

# API Gateway Configuration
variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

variable "api_gateway_throttle_rate_limit" {
  description = "API Gateway throttle rate limit"
  type        = number
  default     = 1000
}

variable "api_gateway_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 2000
}

# Cognito Configuration
variable "cognito_password_policy" {
  description = "Cognito password policy configuration"
  type = object({
    minimum_length    = number
    require_lowercase = bool
    require_numbers   = bool
    require_symbols   = bool
    require_uppercase = bool
  })
  default = {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
}

variable "cognito_mfa_configuration" {
  description = "Cognito MFA configuration (OFF, ON, OPTIONAL)"
  type        = string
  default     = "OPTIONAL"
  
  validation {
    condition     = contains(["OFF", "ON", "OPTIONAL"], var.cognito_mfa_configuration)
    error_message = "Cognito MFA configuration must be OFF, ON, or OPTIONAL."
  }
}

# S3 Configuration
variable "s3_versioning_enabled" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "s3_lifecycle_enabled" {
  description = "Enable S3 lifecycle policies"
  type        = bool
  default     = true
}

variable "s3_transition_to_ia_days" {
  description = "Days to transition objects to Infrequent Access"
  type        = number
  default     = 30
}

variable "s3_transition_to_glacier_days" {
  description = "Days to transition objects to Glacier"
  type        = number
  default     = 90
}

variable "s3_expiration_days" {
  description = "Days to expire objects"
  type        = number
  default     = 365
}

# CORS Configuration
variable "cors_allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "Allowed methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
}

variable "cors_allowed_headers" {
  description = "Allowed headers for CORS"
  type        = list(string)
  default     = ["*"]
}

# Monitoring Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing for Lambda functions"
  type        = bool
  default     = true
}

variable "alert_email_addresses" {
  description = "Email addresses for CloudWatch alerts"
  type        = list(string)
  default     = []
}

# VPC Configuration (Optional)
variable "vpc_subnet_ids" {
  description = "VPC subnet IDs for Lambda functions (optional)"
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "VPC security group IDs for Lambda functions (optional)"
  type        = list(string)
  default     = []
}

# Security Configuration
variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

# Cost Optimization
variable "enable_cost_allocation_tags" {
  description = "Enable cost allocation tags"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

# Feature Flags
variable "enable_alexa_integration" {
  description = "Enable Alexa Skills Kit integration"
  type        = bool
  default     = true
}

variable "enable_web_interface" {
  description = "Enable web interface"
  type        = bool
  default     = true
}

variable "enable_voice_recording" {
  description = "Enable voice recording and storage"
  type        = bool
  default     = true
}

variable "enable_analytics" {
  description = "Enable analytics and reporting"
  type        = bool
  default     = true
}

# External Integrations
variable "external_api_endpoints" {
  description = "External API endpoints for integrations"
  type        = map(string)
  default     = {}
}

variable "webhook_urls" {
  description = "Webhook URLs for notifications"
  type        = list(string)
  default     = []
}
