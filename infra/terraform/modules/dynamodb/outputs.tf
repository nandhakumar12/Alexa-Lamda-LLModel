# DynamoDB Module Outputs

output "table_name" {
  description = "Main conversations table name"
  value       = aws_dynamodb_table.conversations.name
}

output "table_arn" {
  description = "Main conversations table ARN"
  value       = aws_dynamodb_table.conversations.arn
}

output "table_stream_arn" {
  description = "Main conversations table stream ARN"
  value       = aws_dynamodb_table.conversations.stream_arn
}

output "user_sessions_table_name" {
  description = "User sessions table name"
  value       = aws_dynamodb_table.user_sessions.name
}

output "user_sessions_table_arn" {
  description = "User sessions table ARN"
  value       = aws_dynamodb_table.user_sessions.arn
}

output "analytics_table_name" {
  description = "Analytics table name"
  value       = aws_dynamodb_table.analytics.name
}

output "analytics_table_arn" {
  description = "Analytics table ARN"
  value       = aws_dynamodb_table.analytics.arn
}

output "kms_key_id" {
  description = "KMS key ID for DynamoDB encryption"
  value       = aws_kms_key.dynamodb.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for DynamoDB encryption"
  value       = aws_kms_key.dynamodb.arn
}

output "table_names" {
  description = "All DynamoDB table names"
  value = {
    conversations  = aws_dynamodb_table.conversations.name
    user_sessions = aws_dynamodb_table.user_sessions.name
    analytics     = aws_dynamodb_table.analytics.name
  }
}

output "table_arns" {
  description = "All DynamoDB table ARNs"
  value = {
    conversations  = aws_dynamodb_table.conversations.arn
    user_sessions = aws_dynamodb_table.user_sessions.arn
    analytics     = aws_dynamodb_table.analytics.arn
  }
}
