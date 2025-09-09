# AWS Secrets Manager Configuration for Voice Assistant AI
# This file defines all secrets used by the application

# JWT Secret for authentication
resource "aws_secretsmanager_secret" "jwt_secret" {
  name                    = "voice-assistant-ai/jwt-secret"
  description             = "JWT signing secret for user authentication"
  recovery_window_in_days = 7

  tags = {
    Name        = "voice-assistant-ai-jwt-secret"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Generate random JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Store JWT secret value
resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = random_password.jwt_secret.result
}

# API Keys and External Service Credentials
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "voice-assistant-ai/api-keys"
  description             = "API keys and external service credentials"
  recovery_window_in_days = 7

  tags = {
    Name        = "voice-assistant-ai-api-keys"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Store API keys (placeholder values - update with real keys)
resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    claude_api_key     = "YOUR_CLAUDE_API_KEY_HERE"
    openai_api_key     = "YOUR_OPENAI_API_KEY_HERE"
    anthropic_api_key  = "YOUR_ANTHROPIC_API_KEY_HERE"
    encryption_key     = random_password.encryption_key.result
  })
}

# Generate encryption key
resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

# Database Credentials (if using RDS in future)
resource "aws_secretsmanager_secret" "database_credentials" {
  name                    = "voice-assistant-ai/database"
  description             = "Database credentials for RDS (if used)"
  recovery_window_in_days = 7

  tags = {
    Name        = "voice-assistant-ai-database"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Store database credentials (placeholder)
resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.db_password.result
    host     = "placeholder-host"
    port     = "5432"
    database = "voice_assistant_ai"
  })
}

# Generate database password
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Application Configuration Secrets
resource "aws_secretsmanager_secret" "app_config" {
  name                    = "voice-assistant-ai/app-config"
  description             = "Application configuration and sensitive settings"
  recovery_window_in_days = 7

  tags = {
    Name        = "voice-assistant-ai-app-config"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Store application configuration
resource "aws_secretsmanager_secret_version" "app_config" {
  secret_id = aws_secretsmanager_secret.app_config.id
  secret_string = jsonencode({
    jwt_algorithm     = "HS256"
    jwt_expiry_hours  = 24
    max_tokens        = 1000
    model_temperature = 0.7
    rate_limit_per_minute = 60
    session_timeout_minutes = 30
  })
}

# Third-party Service Credentials
resource "aws_secretsmanager_secret" "external_services" {
  name                    = "voice-assistant-ai/external-services"
  description             = "Third-party service credentials and webhooks"
  recovery_window_in_days = 7

  tags = {
    Name        = "voice-assistant-ai-external-services"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Store external service credentials (placeholders)
resource "aws_secretsmanager_secret_version" "external_services" {
  secret_id = aws_secretsmanager_secret.external_services.id
  secret_string = jsonencode({
    slack_webhook_url    = "YOUR_SLACK_WEBHOOK_URL"
    discord_webhook_url  = "YOUR_DISCORD_WEBHOOK_URL"
    email_smtp_password  = "YOUR_EMAIL_SMTP_PASSWORD"
    twilio_auth_token    = "YOUR_TWILIO_AUTH_TOKEN"
    stripe_secret_key    = "YOUR_STRIPE_SECRET_KEY"
  })
}

# Outputs for reference
output "secrets_manager_arns" {
  description = "ARNs of all created secrets"
  value = {
    jwt_secret           = aws_secretsmanager_secret.jwt_secret.arn
    api_keys            = aws_secretsmanager_secret.api_keys.arn
    database_credentials = aws_secretsmanager_secret.database_credentials.arn
    app_config          = aws_secretsmanager_secret.app_config.arn
    external_services   = aws_secretsmanager_secret.external_services.arn
  }
}

output "secrets_manager_names" {
  description = "Names of all created secrets"
  value = {
    jwt_secret           = aws_secretsmanager_secret.jwt_secret.name
    api_keys            = aws_secretsmanager_secret.api_keys.name
    database_credentials = aws_secretsmanager_secret.database_credentials.name
    app_config          = aws_secretsmanager_secret.app_config.name
    external_services   = aws_secretsmanager_secret.external_services.name
  }
}

