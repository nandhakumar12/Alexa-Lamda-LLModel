# Lambda Module Outputs

output "chatbot_lambda_arn" {
  description = "Chatbot Lambda function ARN"
  value       = aws_lambda_function.chatbot.arn
}

output "chatbot_lambda_name" {
  description = "Chatbot Lambda function name"
  value       = aws_lambda_function.chatbot.function_name
}

output "auth_lambda_arn" {
  description = "Auth Lambda function ARN"
  value       = aws_lambda_function.auth.arn
}

output "auth_lambda_name" {
  description = "Auth Lambda function name"
  value       = aws_lambda_function.auth.function_name
}

output "monitoring_lambda_arn" {
  description = "Monitoring Lambda function ARN"
  value       = aws_lambda_function.monitoring.arn
}

output "monitoring_lambda_name" {
  description = "Monitoring Lambda function name"
  value       = aws_lambda_function.monitoring.function_name
}

output "execution_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "execution_role_name" {
  description = "Lambda execution role name"
  value       = aws_iam_role.lambda_execution.name
}

output "kms_key_id" {
  description = "KMS key ID for Lambda encryption"
  value       = aws_kms_key.lambda.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for Lambda encryption"
  value       = aws_kms_key.lambda.arn
}

output "log_group_names" {
  description = "CloudWatch log group names"
  value = {
    chatbot    = aws_cloudwatch_log_group.chatbot.name
    auth       = aws_cloudwatch_log_group.auth.name
    monitoring = aws_cloudwatch_log_group.monitoring.name
  }
}

output "log_group_arns" {
  description = "CloudWatch log group ARNs"
  value = {
    chatbot    = aws_cloudwatch_log_group.chatbot.arn
    auth       = aws_cloudwatch_log_group.auth.arn
    monitoring = aws_cloudwatch_log_group.monitoring.arn
  }
}

output "health_check_urls" {
  description = "Health check URLs for Lambda functions"
  value = {
    chatbot    = "https://console.aws.amazon.com/lambda/home?region=${data.aws_region.current.name}#/functions/${aws_lambda_function.chatbot.function_name}"
    auth       = "https://console.aws.amazon.com/lambda/home?region=${data.aws_region.current.name}#/functions/${aws_lambda_function.auth.function_name}"
    monitoring = "https://console.aws.amazon.com/lambda/home?region=${data.aws_region.current.name}#/functions/${aws_lambda_function.monitoring.function_name}"
  }
}
