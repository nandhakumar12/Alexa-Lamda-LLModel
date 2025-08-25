# DynamoDB table for conversation history
resource "aws_dynamodb_table" "conversation_history" {
  name           = "voice-assistant-conversations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "sort_key"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "sort_key"
    type = "S"
  }

  attribute {
    name = "conversation_id"
    type = "S"
  }

  # Global Secondary Index for querying by conversation_id
  global_secondary_index {
    name     = "conversation-id-index"
    hash_key = "conversation_id"
    range_key = "sort_key"
  }

  # TTL for automatic cleanup of old conversations (30 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "VoiceAssistantConversations"
    Environment = "production"
    Project     = "voice-assistant-ai"
  }
}

# DynamoDB table for user preferences and settings
resource "aws_dynamodb_table" "user_preferences" {
  name           = "voice-assistant-user-preferences"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name        = "VoiceAssistantUserPreferences"
    Environment = "production"
    Project     = "voice-assistant-ai"
  }
}

# No API key needed for AWS Bedrock - uses IAM permissions

# Parameter Store for conversation settings
resource "aws_ssm_parameter" "conversation_settings" {
  name  = "/voice-assistant/conversation-settings"
  type  = "String"
  value = jsonencode({
    max_conversation_length = 8
    default_model = "anthropic.claude-3-haiku-20240307-v1:0"
    temperature = 0.7
    max_tokens = 300
    cost_optimization = true
  })
  description = "LLM conversation settings"

  tags = {
    Environment = "production"
    Project     = "voice-assistant-ai"
  }
}

# Output the table names for Lambda environment variables
output "conversation_table_name" {
  value = aws_dynamodb_table.conversation_history.name
}

output "user_preferences_table_name" {
  value = aws_dynamodb_table.user_preferences.name
}
