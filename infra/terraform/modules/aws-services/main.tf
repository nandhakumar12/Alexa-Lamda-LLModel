# AWS Services Integration Module
# Comprehensive integration of AWS services for production-grade voice assistant

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# EventBridge Custom Bus for Voice Assistant Events
resource "aws_cloudwatch_event_bus" "voice_assistant" {
  name = "${var.name_prefix}-event-bus"
  
  tags = var.tags
}

# EventBridge Rules for Different Events
resource "aws_cloudwatch_event_rule" "user_interaction" {
  name           = "${var.name_prefix}-user-interaction"
  description    = "Capture user interaction events"
  event_bus_name = aws_cloudwatch_event_bus.voice_assistant.name

  event_pattern = jsonencode({
    source      = ["voice-assistant"]
    detail-type = ["User Interaction"]
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_rule" "system_error" {
  name           = "${var.name_prefix}-system-error"
  description    = "Capture system error events"
  event_bus_name = aws_cloudwatch_event_bus.voice_assistant.name

  event_pattern = jsonencode({
    source      = ["voice-assistant"]
    detail-type = ["System Error"]
  })

  tags = var.tags
}

# SQS Queues for Async Processing
resource "aws_sqs_queue" "voice_processing" {
  name                       = "${var.name_prefix}-voice-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 300

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

resource "aws_sqs_queue" "analytics_events" {
  name                       = "${var.name_prefix}-analytics-events"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 60

  tags = var.tags
}

# SNS Topics for Notifications
resource "aws_sns_topic" "system_alerts" {
  name = "${var.name_prefix}-system-alerts"
  
  tags = var.tags
}

resource "aws_sns_topic" "user_notifications" {
  name = "${var.name_prefix}-user-notifications"
  
  tags = var.tags
}

# Step Functions for Complex Workflows
resource "aws_sfn_state_machine" "voice_processing_workflow" {
  name     = "${var.name_prefix}-voice-processing"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "Voice Assistant Processing Workflow"
    StartAt = "ProcessVoiceInput"
    States = {
      ProcessVoiceInput = {
        Type     = "Task"
        Resource = var.voice_processing_lambda_arn
        Next     = "AnalyzeIntent"
        Retry = [
          {
            ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 6
            BackoffRate     = 2
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.TaskFailed"]
            Next        = "HandleError"
          }
        ]
      }
      AnalyzeIntent = {
        Type     = "Task"
        Resource = var.intent_analysis_lambda_arn
        Next     = "RouteToService"
        Retry = [
          {
            ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2
          }
        ]
      }
      RouteToService = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.intent"
            StringEquals  = "music"
            Next          = "HandleMusicRequest"
          },
          {
            Variable      = "$.intent"
            StringEquals  = "weather"
            Next          = "HandleWeatherRequest"
          },
          {
            Variable      = "$.intent"
            StringEquals  = "general"
            Next          = "HandleGeneralRequest"
          }
        ]
        Default = "HandleGeneralRequest"
      }
      HandleMusicRequest = {
        Type     = "Task"
        Resource = var.music_service_lambda_arn
        Next     = "GenerateResponse"
      }
      HandleWeatherRequest = {
        Type     = "Task"
        Resource = var.weather_service_lambda_arn
        Next     = "GenerateResponse"
      }
      HandleGeneralRequest = {
        Type     = "Task"
        Resource = var.llm_service_lambda_arn
        Next     = "GenerateResponse"
      }
      GenerateResponse = {
        Type     = "Task"
        Resource = var.response_generation_lambda_arn
        Next     = "LogInteraction"
      }
      LogInteraction = {
        Type     = "Task"
        Resource = var.logging_lambda_arn
        End      = true
      }
      HandleError = {
        Type = "Task"
        Resource = var.error_handler_lambda_arn
        End = true
      }
    }
  })

  tags = var.tags
}

# IAM Role for Step Functions
resource "aws_iam_role" "step_functions_role" {
  name = "${var.name_prefix}-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "step_functions_policy" {
  role = aws_iam_role.step_functions_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          var.voice_processing_lambda_arn,
          var.intent_analysis_lambda_arn,
          var.music_service_lambda_arn,
          var.weather_service_lambda_arn,
          var.llm_service_lambda_arn,
          var.response_generation_lambda_arn,
          var.logging_lambda_arn,
          var.error_handler_lambda_arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Dashboards
resource "aws_cloudwatch_dashboard" "voice_assistant" {
  dashboard_name = "${var.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", var.chatbot_function_name],
            [".", "Errors", ".", "."],
            [".", "Invocations", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Performance"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", var.api_gateway_name],
            [".", "Latency", ".", "."],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Gateway Performance"
          period  = 300
        }
      }
    ]
  })
}
