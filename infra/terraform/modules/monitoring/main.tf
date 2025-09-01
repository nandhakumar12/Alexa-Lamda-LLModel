# Comprehensive Monitoring and Observability Module
# X-Ray, CloudWatch Insights, EventBridge, and advanced monitoring

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# X-Ray Tracing
resource "aws_xray_sampling_rule" "voice_assistant" {
  rule_name      = "${var.name_prefix}-sampling-rule"
  priority       = 9000
  version        = 1
  reservoir_size = 1
  fixed_rate     = 0.1
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_name   = "*"
  service_type   = "*"
  resource_arn   = "*"

  tags = var.tags
}

# CloudWatch Insights Queries
resource "aws_cloudwatch_query_definition" "error_analysis" {
  name = "${var.name_prefix}-error-analysis"

  log_group_names = [
    "/aws/lambda/${var.chatbot_function_name}",
    "/aws/apigateway/${var.api_gateway_name}"
  ]

  query_string = <<EOF
fields @timestamp, @message, @requestId
| filter @message like /ERROR/
| stats count() by bin(5m)
| sort @timestamp desc
EOF
}

resource "aws_cloudwatch_query_definition" "performance_analysis" {
  name = "${var.name_prefix}-performance-analysis"

  log_group_names = [
    "/aws/lambda/${var.chatbot_function_name}"
  ]

  query_string = <<EOF
fields @timestamp, @duration, @billedDuration, @memorySize, @maxMemoryUsed
| filter @type = "REPORT"
| stats avg(@duration), max(@duration), min(@duration) by bin(5m)
| sort @timestamp desc
EOF
}

resource "aws_cloudwatch_query_definition" "user_interaction_analysis" {
  name = "${var.name_prefix}-user-interactions"

  log_group_names = [
    "/aws/lambda/${var.chatbot_function_name}"
  ]

  query_string = <<EOF
fields @timestamp, @message
| filter @message like /user_id/
| parse @message "user_id: *" as user_id
| stats count() by user_id
| sort count desc
| limit 100
EOF
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  alarm_name          = "${var.name_prefix}-lambda-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors lambda error rate"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = var.chatbot_function_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.name_prefix}-lambda-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = "10000"  # 10 seconds
  alarm_description   = "This metric monitors lambda duration"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = var.chatbot_function_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_4xx_errors" {
  alarm_name          = "${var.name_prefix}-api-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "20"
  alarm_description   = "This metric monitors API Gateway 4XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ApiName = var.api_gateway_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx_errors" {
  alarm_name          = "${var.name_prefix}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors API Gateway 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ApiName = var.api_gateway_name
  }

  tags = var.tags
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.name_prefix}-alerts"
  
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Custom Metrics
resource "aws_cloudwatch_log_metric_filter" "user_interactions" {
  name           = "${var.name_prefix}-user-interactions"
  log_group_name = "/aws/lambda/${var.chatbot_function_name}"
  pattern        = "[timestamp, request_id, level=\"INFO\", message=\"User interaction:\", user_id, intent, ...]"

  metric_transformation {
    name      = "UserInteractions"
    namespace = "VoiceAssistant/Usage"
    value     = "1"
    
    default_value = "0"
  }
}

resource "aws_cloudwatch_log_metric_filter" "llm_requests" {
  name           = "${var.name_prefix}-llm-requests"
  log_group_name = "/aws/lambda/${var.chatbot_function_name}"
  pattern        = "[timestamp, request_id, level=\"INFO\", message=\"LLM request:\", ...]"

  metric_transformation {
    name      = "LLMRequests"
    namespace = "VoiceAssistant/AI"
    value     = "1"
    
    default_value = "0"
  }
}

resource "aws_cloudwatch_log_metric_filter" "voice_processing" {
  name           = "${var.name_prefix}-voice-processing"
  log_group_name = "/aws/lambda/${var.chatbot_function_name}"
  pattern        = "[timestamp, request_id, level=\"INFO\", message=\"Voice processed:\", duration, ...]"

  metric_transformation {
    name      = "VoiceProcessingDuration"
    namespace = "VoiceAssistant/Performance"
    value     = "$duration"
    
    default_value = "0"
  }
}

# Enhanced CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "comprehensive" {
  dashboard_name = "${var.name_prefix}-comprehensive-dashboard"

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
            [".", "Invocations", ".", "."],
            [".", "Throttles", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Performance Metrics"
          period  = 300
          stat    = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
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
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["VoiceAssistant/Usage", "UserInteractions"],
            ["VoiceAssistant/AI", "LLMRequests"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Usage Metrics"
          period  = 300
          stat    = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["VoiceAssistant/Performance", "VoiceProcessingDuration"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Voice Processing Performance"
          period  = 300
          stat    = "Average"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", var.dynamodb_table_name],
            [".", "ConsumedWriteCapacityUnits", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB Capacity"
          period  = 300
          stat    = "Sum"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '/aws/lambda/${var.chatbot_function_name}' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 100"
          region  = var.aws_region
          title   = "Recent Errors"
          view    = "table"
        }
      }
    ]
  })
}

# EventBridge Rules for Monitoring
resource "aws_cloudwatch_event_rule" "lambda_errors" {
  name        = "${var.name_prefix}-lambda-errors"
  description = "Capture Lambda function errors"

  event_pattern = jsonencode({
    source      = ["aws.lambda"]
    detail-type = ["Lambda Function Invocation Result - Failure"]
    detail = {
      functionName = [var.chatbot_function_name]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "lambda_errors_sns" {
  rule      = aws_cloudwatch_event_rule.lambda_errors.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.alerts.arn
}

# Application Insights
resource "aws_applicationinsights_application" "voice_assistant" {
  resource_group_name = aws_resourcegroups_group.voice_assistant.name
  auto_create         = true
  auto_config_enabled = true
  
  tags = var.tags
}

resource "aws_resourcegroups_group" "voice_assistant" {
  name = "${var.name_prefix}-resources"

  resource_query {
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [
        {
          Key    = "Project"
          Values = [var.name_prefix]
        }
      ]
    })
  }

  tags = var.tags
}
