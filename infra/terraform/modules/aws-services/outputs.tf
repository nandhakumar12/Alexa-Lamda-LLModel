# Outputs for AWS Services Module

# EventBridge
output "event_bus_name" {
  description = "Name of the custom EventBridge event bus"
  value       = aws_cloudwatch_event_bus.voice_assistant.name
}

output "event_bus_arn" {
  description = "ARN of the custom EventBridge event bus"
  value       = aws_cloudwatch_event_bus.voice_assistant.arn
}

# SQS
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

output "analytics_events_queue_url" {
  description = "URL of the analytics events SQS queue"
  value       = aws_sqs_queue.analytics_events.url
}

output "analytics_events_queue_arn" {
  description = "ARN of the analytics events SQS queue"
  value       = aws_sqs_queue.analytics_events.arn
}

# SNS
output "system_alerts_topic_arn" {
  description = "ARN of the system alerts SNS topic"
  value       = aws_sns_topic.system_alerts.arn
}

output "user_notifications_topic_arn" {
  description = "ARN of the user notifications SNS topic"
  value       = aws_sns_topic.user_notifications.arn
}

# Step Functions
output "step_function_arn" {
  description = "ARN of the voice processing Step Functions state machine"
  value       = aws_sfn_state_machine.voice_processing_workflow.arn
}

output "step_function_name" {
  description = "Name of the voice processing Step Functions state machine"
  value       = aws_sfn_state_machine.voice_processing_workflow.name
}

# CloudWatch
output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.voice_assistant.dashboard_name}"
}

# EventBridge Rules
output "user_interaction_rule_arn" {
  description = "ARN of the user interaction EventBridge rule"
  value       = aws_cloudwatch_event_rule.user_interaction.arn
}

output "system_error_rule_arn" {
  description = "ARN of the system error EventBridge rule"
  value       = aws_cloudwatch_event_rule.system_error.arn
}
