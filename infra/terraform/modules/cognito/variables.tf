# Voice Assistant AI - Cognito Module Variables

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "domain_name" {
  description = "Domain name for Cognito hosted UI"
  type        = string
}

variable "callback_urls" {
  description = "List of allowed callback URLs"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "logout_urls" {
  description = "List of allowed logout URLs"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "pre_authentication_lambda_arn" {
  description = "ARN of the pre-authentication Lambda function"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
