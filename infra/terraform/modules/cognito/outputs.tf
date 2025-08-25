# Voice Assistant AI - Cognito Module Outputs

output "user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.arn
}

output "user_pool_endpoint" {
  description = "Endpoint of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.endpoint
}

output "user_pool_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.main.id
}

output "user_pool_client_secret" {
  description = "Secret of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.main.client_secret
  sensitive   = true
}

output "identity_pool_id" {
  description = "ID of the Cognito Identity Pool"
  value       = aws_cognito_identity_pool.main.id
}

output "identity_pool_arn" {
  description = "ARN of the Cognito Identity Pool"
  value       = aws_cognito_identity_pool.main.arn
}

output "authenticated_role_arn" {
  description = "ARN of the authenticated IAM role"
  value       = aws_iam_role.authenticated.arn
}

output "domain_name" {
  description = "Domain name for Cognito hosted UI"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "hosted_ui_url" {
  description = "URL for Cognito hosted UI"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
}
