# Outputs for Enhanced EventBridge Module

# EventBridge Outputs
output "event_bus_name" {
  description = "Name of the custom EventBridge event bus"
  value       = aws_cloudwatch_event_bus.ai_assistant.name
}

output "event_bus_arn" {
  description = "ARN of the custom EventBridge event bus"
  value       = aws_cloudwatch_event_bus.ai_assistant.arn
}

output "schema_registry_name" {
  description = "Name of the EventBridge schema registry"
  value       = aws_schemas_registry.ai_assistant.name
}

output "schema_registry_arn" {
  description = "ARN of the EventBridge schema registry"
  value       = aws_schemas_registry.ai_assistant.arn
}

# SQS Queue Outputs
output "voice_processing_queue_url" {
  description = "URL of the voice processing SQS queue"
  value       = aws_sqs_queue.voice_processing.url
}

output "voice_processing_queue_arn" {
  description = "ARN of the voice processing SQS queue"
  value       = aws_sqs_queue.voice_processing.arn
}

output "voice_processing_dlq_url" {
  description = "URL of the voice processing dead letter queue"
  value       = aws_sqs_queue.voice_processing_dlq.url
}

output "voice_processing_dlq_arn" {
  description = "ARN of the voice processing dead letter queue"
  value       = aws_sqs_queue.voice_processing_dlq.arn
}

output "llm_processing_queue_url" {
  description = "URL of the LLM processing SQS queue"
  value       = aws_sqs_queue.llm_processing.url
}

output "llm_processing_queue_arn" {
  description = "ARN of the LLM processing SQS queue"
  value       = aws_sqs_queue.llm_processing.arn
}

output "llm_processing_dlq_url" {
  description = "URL of the LLM processing dead letter queue"
  value       = aws_sqs_queue.llm_processing_dlq.url
}

output "llm_processing_dlq_arn" {
  description = "ARN of the LLM processing dead letter queue"
  value       = aws_sqs_queue.llm_processing_dlq.arn
}

output "analytics_processing_queue_url" {
  description = "URL of the analytics processing SQS queue"
  value       = aws_sqs_queue.analytics_processing.url
}

output "analytics_processing_queue_arn" {
  description = "ARN of the analytics processing SQS queue"
  value       = aws_sqs_queue.analytics_processing.arn
}

# SNS Topic Outputs
output "user_alerts_topic_arn" {
  description = "ARN of the user alerts SNS topic"
  value       = aws_sns_topic.user_alerts.arn
}

output "system_alerts_topic_arn" {
  description = "ARN of the system alerts SNS topic"
  value       = aws_sns_topic.system_alerts.arn
}

output "integration_events_topic_arn" {
  description = "ARN of the integration events SNS topic"
  value       = aws_sns_topic.integration_events.arn
}

# EventBridge Rule Outputs
output "user_voice_interaction_rule_arn" {
  description = "ARN of the user voice interaction EventBridge rule"
  value       = aws_cloudwatch_event_rule.user_voice_interaction.arn
}

output "user_text_interaction_rule_arn" {
  description = "ARN of the user text interaction EventBridge rule"
  value       = aws_cloudwatch_event_rule.user_text_interaction.arn
}

output "ai_response_generated_rule_arn" {
  description = "ARN of the AI response generated EventBridge rule"
  value       = aws_cloudwatch_event_rule.ai_response_generated.arn
}

output "system_errors_rule_arn" {
  description = "ARN of the system errors EventBridge rule"
  value       = aws_cloudwatch_event_rule.system_errors.arn
}

output "high_priority_events_rule_arn" {
  description = "ARN of the high priority events EventBridge rule"
  value       = aws_cloudwatch_event_rule.high_priority_events.arn
}

output "user_behavior_analytics_rule_arn" {
  description = "ARN of the user behavior analytics EventBridge rule"
  value       = aws_cloudwatch_event_rule.user_behavior_analytics.arn
}

# IAM Policy Outputs
output "eventbridge_publish_policy_arn" {
  description = "ARN of the EventBridge publish IAM policy"
  value       = aws_iam_policy.eventbridge_publish.arn
}

output "sqs_access_policy_arn" {
  description = "ARN of the SQS access IAM policy"
  value       = aws_iam_policy.sqs_access.arn
}

# Schema Outputs
output "user_interaction_schema_arn" {
  description = "ARN of the user interaction event schema"
  value       = aws_schemas_schema.user_interaction.arn
}

output "ai_response_schema_arn" {
  description = "ARN of the AI response event schema"
  value       = aws_schemas_schema.ai_response.arn
}

# Configuration Outputs for Lambda Functions
output "eventbridge_config" {
  description = "EventBridge configuration for Lambda functions"
  value = {
    event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
    event_bus_arn  = aws_cloudwatch_event_bus.ai_assistant.arn
    
    queues = {
      voice_processing = {
        url = aws_sqs_queue.voice_processing.url
        arn = aws_sqs_queue.voice_processing.arn
      }
      llm_processing = {
        url = aws_sqs_queue.llm_processing.url
        arn = aws_sqs_queue.llm_processing.arn
      }
      analytics_processing = {
        url = aws_sqs_queue.analytics_processing.url
        arn = aws_sqs_queue.analytics_processing.arn
      }
    }
    
    topics = {
      user_alerts = {
        arn = aws_sns_topic.user_alerts.arn
      }
      system_alerts = {
        arn = aws_sns_topic.system_alerts.arn
      }
      integration_events = {
        arn = aws_sns_topic.integration_events.arn
      }
    }
    
    schemas = {
      user_interaction = aws_schemas_schema.user_interaction.name
      ai_response      = aws_schemas_schema.ai_response.name
    }
  }
  sensitive = false
}

# Environment Variables for Applications
output "environment_variables" {
  description = "Environment variables for applications"
  value = {
    EVENTBRIDGE_BUS_NAME                = aws_cloudwatch_event_bus.ai_assistant.name
    VOICE_PROCESSING_QUEUE_URL          = aws_sqs_queue.voice_processing.url
    LLM_PROCESSING_QUEUE_URL            = aws_sqs_queue.llm_processing.url
    ANALYTICS_PROCESSING_QUEUE_URL      = aws_sqs_queue.analytics_processing.url
    USER_ALERTS_TOPIC_ARN               = aws_sns_topic.user_alerts.arn
    SYSTEM_ALERTS_TOPIC_ARN             = aws_sns_topic.system_alerts.arn
    INTEGRATION_EVENTS_TOPIC_ARN        = aws_sns_topic.integration_events.arn
    SCHEMA_REGISTRY_NAME                = aws_schemas_registry.ai_assistant.name
  }
  sensitive = false
}

# Monitoring and Observability Outputs
output "monitoring_config" {
  description = "Monitoring configuration for EventBridge resources"
  value = {
    event_bus_metrics = {
      namespace = "AWS/Events"
      dimensions = {
        EventBusName = aws_cloudwatch_event_bus.ai_assistant.name
      }
    }
    
    sqs_metrics = {
      namespace = "AWS/SQS"
      queue_names = [
        aws_sqs_queue.voice_processing.name,
        aws_sqs_queue.llm_processing.name,
        aws_sqs_queue.analytics_processing.name
      ]
    }
    
    sns_metrics = {
      namespace = "AWS/SNS"
      topic_names = [
        aws_sns_topic.user_alerts.name,
        aws_sns_topic.system_alerts.name,
        aws_sns_topic.integration_events.name
      ]
    }
  }
  sensitive = false
}

# Integration Endpoints
output "integration_endpoints" {
  description = "Integration endpoints for external services"
  value = {
    eventbridge_api_endpoint = "https://events.${data.aws_region.current.name}.amazonaws.com"
    sqs_api_endpoint        = "https://sqs.${data.aws_region.current.name}.amazonaws.com"
    sns_api_endpoint        = "https://sns.${data.aws_region.current.name}.amazonaws.com"
  }
  sensitive = false
}

# Security Configuration
output "security_config" {
  description = "Security configuration for EventBridge resources"
  value = {
    iam_policies = {
      eventbridge_publish = aws_iam_policy.eventbridge_publish.arn
      sqs_access         = aws_iam_policy.sqs_access.arn
    }
    
    encryption = {
      kms_key_id = var.kms_key_id
      enabled    = var.enable_encryption
    }
    
    access_control = {
      cross_account_enabled = var.enable_cross_account_access
      trusted_accounts     = var.trusted_accounts
    }
  }
  sensitive = false
}

# Data source for current AWS region
data "aws_region" "current" {}
