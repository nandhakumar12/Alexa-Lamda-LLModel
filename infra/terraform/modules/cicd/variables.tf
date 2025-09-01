# Variables for CI/CD Module

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "voice-ai"
}

variable "suffix" {
  description = "Suffix for resource names"
  type        = string
  default     = "prod"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "nandhakumar12"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "Alexa-Lamda-LLModel"
}

variable "github_branch" {
  description = "GitHub branch to monitor"
  type        = string
  default     = "main"
}

variable "notification_email" {
  description = "Email for pipeline notifications"
  type        = string
  default     = ""
}

variable "enable_manual_approval" {
  description = "Enable manual approval before production deployment"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "voice-assistant-ai"
    ManagedBy   = "terraform"
  }
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}
