# Voice Assistant AI - Lex Module Outputs

output "bot_id" {
  description = "ID of the Lex bot"
  value       = aws_lexv2models_bot.main.id
}

output "bot_arn" {
  description = "ARN of the Lex bot"
  value       = aws_lexv2models_bot.main.arn
}

output "bot_name" {
  description = "Name of the Lex bot"
  value       = aws_lexv2models_bot.main.name
}

output "bot_version" {
  description = "Version of the Lex bot"
  value       = aws_lexv2models_bot_version.main.bot_version
}

# Bot alias outputs commented out as alias creation is manual
# output "bot_alias_id" {
#   description = "ID of the Lex bot alias"
#   value       = aws_lexv2models_bot_alias.main.bot_alias_id
# }

# output "bot_alias_arn" {
#   description = "ARN of the Lex bot alias"
#   value       = aws_lexv2models_bot_alias.main.arn
# }

output "bot_locale_id" {
  description = "Locale ID of the Lex bot"
  value       = aws_lexv2models_bot_locale.main.locale_id
}

output "intent_id" {
  description = "ID of the main intent"
  value       = aws_lexv2models_intent.main.intent_id
}
