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

# SonarQube Configuration Variables
variable "sonar_host_url" {
  description = "SonarQube server URL"
  type        = string
  default     = "https://sonarcloud.io"
}

variable "sonar_token" {
  description = "SonarQube token for authentication (stored in Secrets Manager)"
  type        = string
  default     = "voice-assistant-ai/sonar-token"
}

variable "sonar_organization" {
  description = "SonarQube organization key"
  type        = string
  default     = "voice-assistant-ai-org"
}

variable "enable_sonarqube" {
  description = "Enable SonarQube analysis in the pipeline"
  type        = bool
  default     = true
}
