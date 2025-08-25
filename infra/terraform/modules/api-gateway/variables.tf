# API Gateway Module Variables

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

variable "chatbot_lambda_arn" {
  description = "Chatbot Lambda function ARN"
  type        = string
}

variable "auth_lambda_arn" {
  description = "Auth Lambda function ARN"
  type        = string
}

variable "monitoring_lambda_arn" {
  description = "Monitoring Lambda function ARN"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN"
  type        = string
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "throttle_rate_limit" {
  description = "API Gateway throttle rate limit"
  type        = number
  default     = 1000
}

variable "throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 2000
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
