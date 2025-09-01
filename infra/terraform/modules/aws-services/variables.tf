# Variables for AWS Services Module

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Lambda Function ARNs for Step Functions
variable "voice_processing_lambda_arn" {
  description = "ARN of the voice processing Lambda function"
  type        = string
  default     = ""
}

variable "intent_analysis_lambda_arn" {
  description = "ARN of the intent analysis Lambda function"
  type        = string
  default     = ""
}

variable "music_service_lambda_arn" {
  description = "ARN of the music service Lambda function"
  type        = string
  default     = ""
}

variable "weather_service_lambda_arn" {
  description = "ARN of the weather service Lambda function"
  type        = string
  default     = ""
}

variable "llm_service_lambda_arn" {
  description = "ARN of the LLM service Lambda function"
  type        = string
  default     = ""
}

variable "response_generation_lambda_arn" {
  description = "ARN of the response generation Lambda function"
  type        = string
  default     = ""
}

variable "logging_lambda_arn" {
  description = "ARN of the logging Lambda function"
  type        = string
  default     = ""
}

variable "error_handler_lambda_arn" {
  description = "ARN of the error handler Lambda function"
  type        = string
  default     = ""
}

# Monitoring Variables
variable "chatbot_function_name" {
  description = "Name of the main chatbot Lambda function"
  type        = string
  default     = ""
}

variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = ""
}

# Notification Settings
variable "alert_email" {
  description = "Email address for system alerts"
  type        = string
  default     = ""
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

# SQS Settings
variable "enable_dlq" {
  description = "Enable Dead Letter Queue for SQS"
  type        = bool
  default     = true
}

variable "message_retention_days" {
  description = "Message retention period in days"
  type        = number
  default     = 14
}

# Step Functions Settings
variable "enable_step_functions" {
  description = "Enable Step Functions workflow"
  type        = bool
  default     = true
}

# EventBridge Settings
variable "enable_custom_event_bus" {
  description = "Enable custom EventBridge event bus"
  type        = bool
  default     = true
}
