# Variables for Enhanced EventBridge Module

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "priority_notification_targets" {
  description = "List of ARNs for high-priority notification targets"
  type        = list(string)
  default     = []
}

variable "enable_cross_account_access" {
  description = "Enable cross-account access for EventBridge"
  type        = bool
  default     = false
}

variable "trusted_accounts" {
  description = "List of trusted AWS account IDs for cross-account access"
  type        = list(string)
  default     = []
}

variable "retention_days" {
  description = "Number of days to retain events in CloudWatch Logs"
  type        = number
  default     = 14
}

variable "enable_dlq" {
  description = "Enable Dead Letter Queues for SQS"
  type        = bool
  default     = true
}

variable "voice_processing_timeout" {
  description = "Timeout for voice processing in seconds"
  type        = number
  default     = 300
}

variable "llm_processing_timeout" {
  description = "Timeout for LLM processing in seconds"
  type        = number
  default     = 900
}

variable "analytics_processing_timeout" {
  description = "Timeout for analytics processing in seconds"
  type        = number
  default     = 180
}

variable "enable_encryption" {
  description = "Enable encryption for SQS queues and SNS topics"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (if enable_encryption is true)"
  type        = string
  default     = "alias/aws/sqs"
}

variable "max_receive_count" {
  description = "Maximum number of times a message can be received before moving to DLQ"
  type        = number
  default     = 3
}

variable "enable_fifo_queues" {
  description = "Enable FIFO queues for ordered processing"
  type        = bool
  default     = false
}

variable "enable_content_based_deduplication" {
  description = "Enable content-based deduplication for FIFO queues"
  type        = bool
  default     = true
}

variable "webhook_endpoints" {
  description = "List of webhook endpoints for external integrations"
  type = list(object({
    name     = string
    url      = string
    headers  = map(string)
    enabled  = bool
  }))
  default = []
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "email_notifications" {
  description = "Email addresses for system notifications"
  type        = list(string)
  default     = []
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing for EventBridge"
  type        = bool
  default     = true
}

variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "custom_event_patterns" {
  description = "Custom event patterns for additional rules"
  type = list(object({
    name         = string
    description  = string
    event_pattern = string
    targets      = list(string)
  }))
  default = []
}

variable "integration_services" {
  description = "External services to integrate with EventBridge"
  type = object({
    enable_salesforce = bool
    enable_zendesk    = bool
    enable_datadog    = bool
    enable_pagerduty  = bool
  })
  default = {
    enable_salesforce = false
    enable_zendesk    = false
    enable_datadog    = false
    enable_pagerduty  = false
  }
}

variable "event_replay_config" {
  description = "Configuration for event replay functionality"
  type = object({
    enable_replay     = bool
    retention_days    = number
    replay_queue_name = string
  })
  default = {
    enable_replay     = false
    retention_days    = 7
    replay_queue_name = "event-replay"
  }
}

variable "rate_limiting" {
  description = "Rate limiting configuration for EventBridge rules"
  type = object({
    enable_rate_limiting = bool
    max_events_per_second = number
    burst_limit          = number
  })
  default = {
    enable_rate_limiting = true
    max_events_per_second = 100
    burst_limit          = 200
  }
}

variable "archive_config" {
  description = "Configuration for event archiving"
  type = object({
    enable_archiving    = bool
    archive_name        = string
    retention_days      = number
    event_pattern       = string
  })
  default = {
    enable_archiving = false
    archive_name     = "ai-assistant-events"
    retention_days   = 365
    event_pattern    = "{}"
  }
}

variable "disaster_recovery" {
  description = "Disaster recovery configuration"
  type = object({
    enable_cross_region_replication = bool
    backup_region                   = string
    enable_automatic_failover       = bool
  })
  default = {
    enable_cross_region_replication = false
    backup_region                   = "us-west-2"
    enable_automatic_failover       = false
  }
}

variable "cost_optimization" {
  description = "Cost optimization settings"
  type = object({
    enable_scheduled_scaling = bool
    off_peak_hours          = list(string)
    weekend_scaling         = bool
  })
  default = {
    enable_scheduled_scaling = false
    off_peak_hours          = ["22:00-06:00"]
    weekend_scaling         = true
  }
}

variable "compliance_settings" {
  description = "Compliance and security settings"
  type = object({
    enable_audit_logging    = bool
    enable_data_residency   = bool
    allowed_regions         = list(string)
    enable_pii_detection    = bool
  })
  default = {
    enable_audit_logging  = true
    enable_data_residency = false
    allowed_regions       = ["us-east-1", "us-west-2"]
    enable_pii_detection  = false
  }
}

variable "performance_tuning" {
  description = "Performance tuning parameters"
  type = object({
    batch_size              = number
    parallel_processing     = bool
    enable_batch_processing = bool
    max_batch_window        = number
  })
  default = {
    batch_size              = 10
    parallel_processing     = true
    enable_batch_processing = true
    max_batch_window        = 5
  }
}
