# Lambda Module Variables

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "lex_bot_id" {
  description = "Amazon Lex bot ID"
  type        = string
}

variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "lambda_reserved_concurrency" {
  description = "Reserved concurrency for Lambda functions"
  type        = number
  default     = 10
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}

variable "vpc_subnet_ids" {
  description = "VPC subnet IDs for Lambda functions"
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "VPC security group IDs for Lambda functions"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
