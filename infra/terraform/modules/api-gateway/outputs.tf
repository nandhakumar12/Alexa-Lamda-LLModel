# API Gateway Module Outputs

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.main.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.main.stage_name}"
}

output "stage_name" {
  description = "API Gateway stage name"
  value       = aws_api_gateway_stage.main.stage_name
}

output "execution_arn" {
  description = "API Gateway execution ARN"
  value       = aws_api_gateway_rest_api.main.execution_arn
}

output "execution_role_arn" {
  description = "API Gateway execution role ARN (placeholder)"
  value       = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/apigateway-role"
}

output "deployment_id" {
  description = "API Gateway deployment ID"
  value       = aws_api_gateway_deployment.main.id
}

output "rest_api_arn" {
  description = "API Gateway REST API ARN"
  value       = aws_api_gateway_rest_api.main.arn
}

output "authorizer_id" {
  description = "Cognito authorizer ID"
  value       = aws_api_gateway_authorizer.cognito.id
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.api_gateway.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.api_gateway.arn
}
