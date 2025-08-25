# Voice Assistant AI - Lex Module Variables

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bot_locale" {
  description = "Locale for the Lex bot"
  type        = string
  default     = "en_US"
}

variable "fulfillment_lambda_arn" {
  description = "ARN of the Lambda function for fulfillment"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
