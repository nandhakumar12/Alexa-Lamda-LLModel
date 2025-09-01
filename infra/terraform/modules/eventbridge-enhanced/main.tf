# Enhanced EventBridge Module for AI Assistant
# Production-grade event-driven architecture

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Custom EventBridge Bus for AI Assistant
resource "aws_cloudwatch_event_bus" "ai_assistant" {
  name = "${var.name_prefix}-ai-assistant-bus"
  
  tags = merge(var.tags, {
    Component = "EventBridge"
    Purpose   = "AI Assistant Event Hub"
  })
}

# EventBridge Schema Registry
resource "aws_schemas_registry" "ai_assistant" {
  name        = "${var.name_prefix}-ai-schemas"
  description = "Schema registry for AI Assistant events"
  
  tags = var.tags
}

# Event Schemas
resource "aws_schemas_schema" "user_interaction" {
  name          = "UserInteractionEvent"
  registry_name = aws_schemas_registry.ai_assistant.name
  type          = "JSONSchemaDraft4"
  description   = "Schema for user interaction events"

  content = jsonencode({
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
      "userId": {
        "type": "string",
        "description": "Unique user identifier"
      },
      "sessionId": {
        "type": "string",
        "description": "Session identifier"
      },
      "interactionType": {
        "type": "string",
        "enum": ["voice", "text", "gesture"],
        "description": "Type of user interaction"
      },
      "message": {
        "type": "string",
        "description": "User message content"
      },
      "timestamp": {
        "type": "string",
        "format": "date-time",
        "description": "Event timestamp"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "deviceType": {"type": "string"},
          "location": {"type": "string"},
          "language": {"type": "string"},
          "confidence": {"type": "number"}
        }
      }
    },
    "required": ["userId", "sessionId", "interactionType", "timestamp"]
  })
}

resource "aws_schemas_schema" "ai_response" {
  name          = "AIResponseEvent"
  registry_name = aws_schemas_registry.ai_assistant.name
  type          = "JSONSchemaDraft4"
  description   = "Schema for AI response events"

  content = jsonencode({
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
      "responseId": {"type": "string"},
      "userId": {"type": "string"},
      "sessionId": {"type": "string"},
      "responseType": {
        "type": "string",
        "enum": ["text", "audio", "action"]
      },
      "content": {"type": "string"},
      "confidence": {"type": "number"},
      "processingTime": {"type": "number"},
      "aiModel": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"}
    },
    "required": ["responseId", "userId", "sessionId", "responseType", "timestamp"]
  })
}

# SQS Queues for Async Processing
resource "aws_sqs_queue" "voice_processing" {
  name                       = "${var.name_prefix}-voice-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 20       # Long polling
  visibility_timeout_seconds = 300      # 5 minutes

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.voice_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = var.tags
}

resource "aws_sqs_queue" "voice_processing_dlq" {
  name                       = "${var.name_prefix}-voice-processing-dlq"
  message_retention_seconds  = 1209600  # 14 days
  
  tags = var.tags
}

resource "aws_sqs_queue" "llm_processing" {
  name                       = "${var.name_prefix}-llm-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600
  receive_wait_time_seconds  = 20
  visibility_timeout_seconds = 900      # 15 minutes for LLM processing

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.llm_processing_dlq.arn
    maxReceiveCount     = 2
  })

  tags = var.tags
}

resource "aws_sqs_queue" "llm_processing_dlq" {
  name                       = "${var.name_prefix}-llm-processing-dlq"
  message_retention_seconds  = 1209600
  
  tags = var.tags
}

resource "aws_sqs_queue" "analytics_processing" {
  name                       = "${var.name_prefix}-analytics-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 604800   # 7 days
  receive_wait_time_seconds  = 20
  visibility_timeout_seconds = 180      # 3 minutes

  tags = var.tags
}

# SNS Topics for Notifications
resource "aws_sns_topic" "user_alerts" {
  name = "${var.name_prefix}-user-alerts"
  
  tags = var.tags
}

resource "aws_sns_topic" "system_alerts" {
  name = "${var.name_prefix}-system-alerts"
  
  tags = var.tags
}

resource "aws_sns_topic" "integration_events" {
  name = "${var.name_prefix}-integration-events"
  
  tags = var.tags
}

# EventBridge Rules for User Interactions
resource "aws_cloudwatch_event_rule" "user_voice_interaction" {
  name           = "${var.name_prefix}-user-voice-interaction"
  description    = "Route voice interactions to processing queue"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["User Interaction"]
    detail = {
      interactionType = ["voice"]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "voice_to_sqs" {
  rule           = aws_cloudwatch_event_rule.user_voice_interaction.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "VoiceProcessingQueue"
  arn            = aws_sqs_queue.voice_processing.arn

  sqs_target {
    message_group_id = "voice-processing"
  }
}

resource "aws_cloudwatch_event_rule" "user_text_interaction" {
  name           = "${var.name_prefix}-user-text-interaction"
  description    = "Route text interactions to LLM processing"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["User Interaction"]
    detail = {
      interactionType = ["text"]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "text_to_llm_queue" {
  rule           = aws_cloudwatch_event_rule.user_text_interaction.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "LLMProcessingQueue"
  arn            = aws_sqs_queue.llm_processing.arn

  sqs_target {
    message_group_id = "llm-processing"
  }
}

# EventBridge Rule for AI Responses
resource "aws_cloudwatch_event_rule" "ai_response_generated" {
  name           = "${var.name_prefix}-ai-response-generated"
  description    = "Handle AI response events"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["AI Response Generated"]
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "response_to_analytics" {
  rule           = aws_cloudwatch_event_rule.ai_response_generated.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "AnalyticsProcessing"
  arn            = aws_sqs_queue.analytics_processing.arn
}

# EventBridge Rule for System Errors
resource "aws_cloudwatch_event_rule" "system_errors" {
  name           = "${var.name_prefix}-system-errors"
  description    = "Capture system errors and failures"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["System Error", "Processing Failure"]
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "errors_to_sns" {
  rule           = aws_cloudwatch_event_rule.system_errors.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "SystemAlertsNotification"
  arn            = aws_sns_topic.system_alerts.arn
}

# EventBridge Rule for High-Priority Events
resource "aws_cloudwatch_event_rule" "high_priority_events" {
  name           = "${var.name_prefix}-high-priority-events"
  description    = "Handle high-priority events requiring immediate attention"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["Emergency Alert", "Security Incident", "System Critical"]
    detail = {
      priority = ["high", "critical"]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "priority_to_multiple_targets" {
  count          = length(var.priority_notification_targets)
  rule           = aws_cloudwatch_event_rule.high_priority_events.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "PriorityTarget${count.index}"
  arn            = var.priority_notification_targets[count.index]
}

# EventBridge Rule for User Behavior Analytics
resource "aws_cloudwatch_event_rule" "user_behavior_analytics" {
  name           = "${var.name_prefix}-user-behavior-analytics"
  description    = "Collect user behavior data for analytics"
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name

  event_pattern = jsonencode({
    source      = ["ai-assistant"]
    detail-type = ["User Interaction", "AI Response Generated", "Session Event"]
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "behavior_to_analytics" {
  rule           = aws_cloudwatch_event_rule.user_behavior_analytics.name
  event_bus_name = aws_cloudwatch_event_bus.ai_assistant.name
  target_id      = "BehaviorAnalytics"
  arn            = aws_sqs_queue.analytics_processing.arn
}

# IAM Policies for EventBridge
resource "aws_iam_policy" "eventbridge_publish" {
  name        = "${var.name_prefix}-eventbridge-publish"
  description = "Allow Lambda functions to publish events to EventBridge"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = [
          aws_cloudwatch_event_bus.ai_assistant.arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "sqs_access" {
  name        = "${var.name_prefix}-sqs-access"
  description = "Allow access to SQS queues for event processing"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.voice_processing.arn,
          aws_sqs_queue.llm_processing.arn,
          aws_sqs_queue.analytics_processing.arn
        ]
      }
    ]
  })
}

# SQS Queue Policies
resource "aws_sqs_queue_policy" "voice_processing_policy" {
  queue_url = aws_sqs_queue.voice_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.voice_processing.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue_policy" "llm_processing_policy" {
  queue_url = aws_sqs_queue.llm_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.llm_processing.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue_policy" "analytics_processing_policy" {
  queue_url = aws_sqs_queue.analytics_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.analytics_processing.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
