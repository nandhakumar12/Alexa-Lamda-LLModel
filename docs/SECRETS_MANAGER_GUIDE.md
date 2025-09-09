# AWS Secrets Manager Configuration Guide

This guide explains how to configure and use AWS Secrets Manager for the Voice Assistant AI project.

## 🔐 Overview

AWS Secrets Manager is used to securely store and manage sensitive information such as:
- JWT signing secrets
- API keys (Claude, OpenAI, etc.)
- Database credentials
- Application configuration
- Third-party service credentials

## 📁 Secret Structure

### 1. JWT Secret
- **Name**: `voice-assistant-ai/jwt-secret`
- **Type**: String
- **Purpose**: JWT token signing and validation
- **Generated**: Automatically by Terraform

### 2. API Keys
- **Name**: `voice-assistant-ai/api-keys`
- **Type**: JSON
- **Purpose**: External API credentials
- **Structure**:
```json
{
  "claude_api_key": "YOUR_CLAUDE_API_KEY_HERE",
  "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
  "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
  "encryption_key": "generated-encryption-key"
}
```

### 3. Database Credentials
- **Name**: `voice-assistant-ai/database`
- **Type**: JSON
- **Purpose**: Database connection credentials
- **Structure**:
```json
{
  "username": "admin",
  "password": "generated-password",
  "host": "placeholder-host",
  "port": "5432",
  "database": "voice_assistant_ai"
}
```

### 4. Application Configuration
- **Name**: `voice-assistant-ai/app-config`
- **Type**: JSON
- **Purpose**: Application settings and configuration
- **Structure**:
```json
{
  "jwt_algorithm": "HS256",
  "jwt_expiry_hours": 24,
  "max_tokens": 1000,
  "model_temperature": 0.7,
  "rate_limit_per_minute": 60,
  "session_timeout_minutes": 30
}
```

### 5. External Services
- **Name**: `voice-assistant-ai/external-services`
- **Type**: JSON
- **Purpose**: Third-party service credentials
- **Structure**:
```json
{
  "slack_webhook_url": "YOUR_SLACK_WEBHOOK_URL",
  "discord_webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
  "email_smtp_password": "YOUR_EMAIL_SMTP_PASSWORD",
  "twilio_auth_token": "YOUR_TWILIO_AUTH_TOKEN",
  "stripe_secret_key": "YOUR_STRIPE_SECRET_KEY"
}
```

## 🚀 Setup Instructions

### 1. Deploy Terraform Configuration

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### 2. Run Secrets Setup Script

```bash
python scripts/setup-secrets.py
```

### 3. Update API Keys

After running the setup script, update the API keys with real values:

```bash
# Update Claude API key
aws secretsmanager update-secret \
  --secret-id voice-assistant-ai/api-keys \
  --secret-string '{
    "claude_api_key": "your-real-claude-api-key",
    "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
    "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
    "encryption_key": "existing-encryption-key"
  }'
```

## 💻 Using Secrets in Lambda Functions

### Python Helper Functions

```python
from shared.secrets_manager import (
    get_jwt_secret,
    get_claude_api_key,
    get_openai_api_key,
    get_encryption_key,
    get_app_config_value
)

# Get JWT secret
jwt_secret = get_jwt_secret()

# Get API keys
claude_key = get_claude_api_key()
openai_key = get_openai_api_key()

# Get app configuration
max_tokens = get_app_config_value('max_tokens', 1000)
temperature = get_app_config_value('model_temperature', 0.7)
```

### Direct AWS SDK Usage

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
api_keys = get_secret('voice-assistant-ai/api-keys')
claude_key = api_keys['claude_api_key']
```

## 🔒 Security Best Practices

### 1. IAM Permissions
- Lambda functions have minimal required permissions
- Secrets are scoped to specific ARNs
- No wildcard permissions for secrets

### 2. Secret Rotation
- JWT secrets can be rotated manually
- API keys should be rotated regularly
- Use AWS Secrets Manager rotation features

### 3. Access Logging
- All secret access is logged in CloudTrail
- Monitor for unusual access patterns
- Set up alerts for failed access attempts

### 4. Environment Separation
- Use different secrets for dev/staging/prod
- Never share secrets between environments
- Use parameter store for non-sensitive config

## 🛠️ Management Commands

### List All Secrets
```bash
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `voice-assistant-ai`)]'
```

### Get Secret Value
```bash
aws secretsmanager get-secret-value --secret-id voice-assistant-ai/jwt-secret
```

### Update Secret
```bash
aws secretsmanager update-secret \
  --secret-id voice-assistant-ai/api-keys \
  --secret-string '{"claude_api_key": "new-key"}'
```

### Delete Secret
```bash
aws secretsmanager delete-secret \
  --secret-id voice-assistant-ai/old-secret \
  --recovery-window-in-days 7
```

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check IAM policies for Lambda execution role
   - Verify secret ARN in policy

2. **Secret Not Found**
   - Verify secret name spelling
   - Check AWS region
   - Ensure secret exists

3. **JSON Parse Error**
   - Verify secret value is valid JSON
   - Check for special characters

4. **Timeout Errors**
   - Check Lambda timeout settings
   - Verify VPC configuration if applicable

### Debug Commands

```bash
# Test secret access
aws secretsmanager get-secret-value --secret-id voice-assistant-ai/jwt-secret

# Check Lambda permissions
aws iam get-role-policy --role-name voice-assistant-ai-prod-lambda-execution-role --policy-name voice-assistant-ai-prod-lambda-execution-policy

# View CloudTrail logs
aws logs filter-log-events --log-group-name CloudTrail --filter-pattern "secretsmanager"
```

## 📊 Monitoring

### CloudWatch Metrics
- Secret access success/failure rates
- Lambda function errors
- API Gateway 4xx/5xx responses

### CloudTrail Events
- `GetSecretValue` API calls
- Secret creation/updates
- Permission denied errors

### Alarms
Set up CloudWatch alarms for:
- Failed secret access attempts
- Lambda function errors
- Unusual API usage patterns

## 🔄 Backup and Recovery

### Backup Strategy
- Secrets are automatically backed up by AWS
- Use AWS Backup for additional protection
- Store critical secrets in multiple regions

### Recovery Process
1. Identify affected secrets
2. Restore from backup if available
3. Update affected applications
4. Test functionality
5. Monitor for issues

## 📚 Additional Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Lambda Environment Variables vs Secrets Manager](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)

