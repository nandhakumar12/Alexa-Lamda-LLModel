# CloudWatch Alarms for Lambda Functions
# Voice Assistant AI - Production Monitoring

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Variables
variable "project_name" {
  description = "Project name"
  type        = string
  default     = "voice-assistant-ai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  type        = string
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  lambda_functions = [
    "chatbot",
    "auth",
    "monitoring"
  ]
}

# Lambda Error Rate Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  count = length(local.lambda_functions)
  
  alarm_name          = "${local.name_prefix}-${local.lambda_functions[count.index]}-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  threshold           = "5"
  alarm_description   = "Lambda function ${local.lambda_functions[count.index]} error rate is too high"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  metric_query {
    id = "e1"
    
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = 300
      stat        = "Sum"
      
      dimensions = {
        FunctionName = "${local.name_prefix}-${local.lambda_functions[count.index]}"
      }
    }
  }

  metric_query {
    id = "i1"
    
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = 300
      stat        = "Sum"
      
      dimensions = {
        FunctionName = "${local.name_prefix}-${local.lambda_functions[count.index]}"
      }
    }
  }

  metric_query {
    id          = "error_rate"
    expression  = "e1/i1*100"
    label       = "Error Rate (%)"
    return_data = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Lambda Duration Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count = length(local.lambda_functions)
  
  alarm_name          = "${local.name_prefix}-${local.lambda_functions[count.index]}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = "10000"  # 10 seconds
  alarm_description   = "Lambda function ${local.lambda_functions[count.index]} duration is too high"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.name_prefix}-${local.lambda_functions[count.index]}"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Lambda Throttle Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  count = length(local.lambda_functions)
  
  alarm_name          = "${local.name_prefix}-${local.lambda_functions[count.index]}-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Lambda function ${local.lambda_functions[count.index]} is being throttled"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.name_prefix}-${local.lambda_functions[count.index]}"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Lambda Concurrent Executions Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_concurrent_executions" {
  count = length(local.lambda_functions)
  
  alarm_name          = "${local.name_prefix}-${local.lambda_functions[count.index]}-concurrent-executions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "50"  # Adjust based on reserved concurrency
  alarm_description   = "Lambda function ${local.lambda_functions[count.index]} concurrent executions are too high"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.name_prefix}-${local.lambda_functions[count.index]}"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Lambda Dead Letter Queue Alarm (if DLQ is configured)
resource "aws_cloudwatch_metric_alarm" "lambda_dlq_messages" {
  count = length(local.lambda_functions)
  
  alarm_name          = "${local.name_prefix}-${local.lambda_functions[count.index]}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfVisibleMessages"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "Messages in DLQ for Lambda function ${local.lambda_functions[count.index]}"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = "${local.name_prefix}-${local.lambda_functions[count.index]}-dlq"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Custom Metric Alarms for Business Logic

# Text Message Processing Errors
resource "aws_cloudwatch_metric_alarm" "text_message_errors" {
  alarm_name          = "${local.name_prefix}-text-message-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TextMessageError"
  namespace           = "VoiceAssistantAI"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "High number of text message processing errors"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Voice Message Processing Errors
resource "aws_cloudwatch_metric_alarm" "voice_message_errors" {
  alarm_name          = "${local.name_prefix}-voice-message-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "VoiceMessageError"
  namespace           = "VoiceAssistantAI"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "High number of voice message processing errors"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Authentication Errors
resource "aws_cloudwatch_metric_alarm" "authentication_errors" {
  alarm_name          = "${local.name_prefix}-authentication-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "AuthenticationError"
  namespace           = "VoiceAssistantAI"
  period              = "300"
  statistic           = "Sum"
  threshold           = "20"
  alarm_description   = "High number of authentication errors"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# System Health Alarm
resource "aws_cloudwatch_metric_alarm" "system_health" {
  alarm_name          = "${local.name_prefix}-system-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "SystemHealth"
  namespace           = "VoiceAssistantAI"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "System health check is failing"
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "breaching"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Composite Alarm for Overall System Health
resource "aws_cloudwatch_composite_alarm" "overall_system_health" {
  alarm_name        = "${local.name_prefix}-overall-system-health"
  alarm_description = "Overall system health based on multiple metrics"
  
  alarm_rule = join(" OR ", [
    "ALARM(${aws_cloudwatch_metric_alarm.lambda_error_rate[0].alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.lambda_error_rate[1].alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.lambda_error_rate[2].alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.system_health.alarm_name})"
  ])
  
  alarm_actions = [var.sns_topic_arn]
  ok_actions    = [var.sns_topic_arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "monitoring"
  }
}

# Outputs
output "alarm_names" {
  description = "Names of created CloudWatch alarms"
  value = concat(
    aws_cloudwatch_metric_alarm.lambda_error_rate[*].alarm_name,
    aws_cloudwatch_metric_alarm.lambda_duration[*].alarm_name,
    aws_cloudwatch_metric_alarm.lambda_throttles[*].alarm_name,
    aws_cloudwatch_metric_alarm.lambda_concurrent_executions[*].alarm_name,
    [
      aws_cloudwatch_metric_alarm.text_message_errors.alarm_name,
      aws_cloudwatch_metric_alarm.voice_message_errors.alarm_name,
      aws_cloudwatch_metric_alarm.authentication_errors.alarm_name,
      aws_cloudwatch_metric_alarm.system_health.alarm_name,
      aws_cloudwatch_composite_alarm.overall_system_health.alarm_name
    ]
  )
}

output "composite_alarm_arn" {
  description = "ARN of the composite alarm"
  value       = aws_cloudwatch_composite_alarm.overall_system_health.arn
}
