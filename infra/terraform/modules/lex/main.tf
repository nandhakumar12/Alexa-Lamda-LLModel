# Voice Assistant AI - Lex Module
# Amazon Lex V2 chatbot configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM role for Lex bot
resource "aws_iam_role" "lex_bot" {
  name = "${var.name_prefix}-lex-bot-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lexv2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

# IAM policy for Lex bot
resource "aws_iam_role_policy" "lex_bot" {
  name = "${var.name_prefix}-lex-bot-policy"
  role = aws_iam_role.lex_bot.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "polly:SynthesizeSpeech",
          "comprehend:DetectSentiment",
          "comprehend:DetectEntities",
          "comprehend:DetectKeyPhrases",
          "comprehend:DetectLanguage",
          "comprehend:DetectSyntax"
        ]
        Resource = "*"
      }
    ]
  })
}

# Note: Lex bot permissions are handled by the inline policy above

# Lex Bot
resource "aws_lexv2models_bot" "main" {
  name     = "${var.name_prefix}-bot"
  role_arn = aws_iam_role.lex_bot.arn

  data_privacy {
    child_directed = false
  }

  idle_session_ttl_in_seconds = 300

  tags = var.tags
}

# Lex Bot Version
resource "aws_lexv2models_bot_version" "main" {
  bot_id = aws_lexv2models_bot.main.id
  locale_specification = {
    (var.bot_locale) = {
      source_bot_version = "DRAFT"
    }
  }

  depends_on = [aws_lexv2models_intent.main]
}

# Lex Bot Locale
resource "aws_lexv2models_bot_locale" "main" {
  bot_id      = aws_lexv2models_bot.main.id
  bot_version = "DRAFT"
  locale_id   = var.bot_locale

  n_lu_intent_confidence_threshold = 0.40

  voice_settings {
    voice_id = "Joanna"
  }
}

# Lex Intent
resource "aws_lexv2models_intent" "main" {
  bot_id      = aws_lexv2models_bot.main.id
  bot_version = "DRAFT"
  locale_id   = aws_lexv2models_bot_locale.main.locale_id
  name        = "VoiceAssistantIntent"

  description = "Main intent for voice assistant interactions"

  sample_utterance {
    utterance = "Hello"
  }

  sample_utterance {
    utterance = "Hi there"
  }

  sample_utterance {
    utterance = "Good morning"
  }

  sample_utterance {
    utterance = "Help me"
  }

  sample_utterance {
    utterance = "What can you do"
  }

  fulfillment_code_hook {
    enabled = true
  }

  dynamic "dialog_code_hook" {
    for_each = var.fulfillment_lambda_arn != "" ? [1] : []
    content {
      enabled = true
    }
  }
}

# Lambda permission for Lex (commented out for now due to dependency issues)
# This can be created manually after deployment if needed
# resource "aws_lambda_permission" "lex" {
#   count         = var.fulfillment_lambda_arn != "" ? 1 : 0
#   statement_id  = "AllowExecutionFromLex"
#   action        = "lambda:InvokeFunction"
#   function_name = var.fulfillment_lambda_arn
#   principal     = "lexv2.amazonaws.com"
#   source_arn    = "${aws_lexv2models_bot.main.arn}/*"
# }

# Note: Lex Bot Alias creation via Terraform is limited in AWS provider
# For now, we'll create the bot and version, and the alias can be created manually
# or via AWS CLI in a post-deployment script
