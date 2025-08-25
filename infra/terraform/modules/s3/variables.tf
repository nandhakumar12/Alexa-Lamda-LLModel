# Voice Assistant AI - S3 Module Variables

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bucket_suffix" {
  description = "Random suffix for bucket names"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "lifecycle_enabled" {
  description = "Enable S3 lifecycle policies"
  type        = bool
  default     = true
}

variable "transition_to_ia_days" {
  description = "Days to transition objects to Infrequent Access"
  type        = number
  default     = 30
}

variable "transition_to_glacier_days" {
  description = "Days to transition objects to Glacier"
  type        = number
  default     = 90
}

variable "expiration_days" {
  description = "Days to expire objects"
  type        = number
  default     = 365
}

variable "cors_allowed_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
