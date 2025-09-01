# IAM role for LLM Lambda function
resource "aws_iam_role" "llm_lambda_role" {
  name = "voice-assistant-llm-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for LLM Lambda function
resource "aws_iam_role_policy" "llm_lambda_policy" {
  name = "voice-assistant-llm-lambda-policy"
  role = aws_iam_role.llm_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ]
        Resource = [
          aws_dynamodb_table.conversation_history.arn,
          "${aws_dynamodb_table.conversation_history.arn}/index/*",
          aws_dynamodb_table.user_preferences.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = [
          aws_ssm_parameter.conversation_settings.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        ]
      }
    ]
  })
}

# Create deployment package for LLM Lambda
data "archive_file" "llm_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/lambda_functions"
  output_path = "${path.module}/llm_lambda_function.zip"
  excludes    = ["__pycache__", "*.pyc"]
}

# LLM Lambda function
resource "aws_lambda_function" "llm_chatbot" {
  filename         = data.archive_file.llm_lambda_zip.output_path
  function_name    = "voice-assistant-llm-chatbot"
  role            = aws_iam_role.llm_lambda_role.arn
  handler         = "llm_chatbot_bedrock.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 512

  source_code_hash = data.archive_file.llm_lambda_zip.output_base64sha256

  environment {
    variables = {
      CONVERSATION_TABLE = aws_dynamodb_table.conversation_history.name
      USER_PREFERENCES_TABLE = aws_dynamodb_table.user_preferences.name
      CONVERSATION_SETTINGS_PARAM = aws_ssm_parameter.conversation_settings.name
      AWS_REGION = "us-east-1"
    }
  }

  tags = {
    Name        = "VoiceAssistantLLMChatbot"
    Environment = "production"
    Project     = "voice-assistant-ai"
  }
}

# CloudWatch Log Group for LLM Lambda
resource "aws_cloudwatch_log_group" "llm_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.llm_chatbot.function_name}"
  retention_in_days = 14

  tags = {
    Environment = "production"
    Project     = "voice-assistant-ai"
  }
}

# API Gateway for LLM Lambda
resource "aws_api_gateway_rest_api" "llm_api" {
  name        = "voice-assistant-llm-api"
  description = "API Gateway for LLM-powered Voice Assistant"
}

# API Gateway resource
resource "aws_api_gateway_resource" "llm_chat" {
  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  parent_id   = aws_api_gateway_rest_api.llm_api.root_resource_id
  path_part   = "chat"
}

# API Gateway method - POST
resource "aws_api_gateway_method" "llm_chat_post" {
  rest_api_id   = aws_api_gateway_rest_api.llm_api.id
  resource_id   = aws_api_gateway_resource.llm_chat.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway method - OPTIONS for CORS
resource "aws_api_gateway_method" "llm_chat_options" {
  rest_api_id   = aws_api_gateway_rest_api.llm_api.id
  resource_id   = aws_api_gateway_resource.llm_chat.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# API Gateway integration - POST
resource "aws_api_gateway_integration" "llm_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  resource_id = aws_api_gateway_resource.llm_chat.id
  http_method = aws_api_gateway_method.llm_chat_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.llm_chatbot.invoke_arn
}

# API Gateway integration - OPTIONS for CORS
resource "aws_api_gateway_integration" "llm_chat_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  resource_id = aws_api_gateway_resource.llm_chat.id
  http_method = aws_api_gateway_method.llm_chat_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# API Gateway method response - OPTIONS
resource "aws_api_gateway_method_response" "llm_chat_options_response" {
  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  resource_id = aws_api_gateway_resource.llm_chat.id
  http_method = aws_api_gateway_method.llm_chat_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# API Gateway integration response - OPTIONS
resource "aws_api_gateway_integration_response" "llm_chat_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  resource_id = aws_api_gateway_resource.llm_chat.id
  http_method = aws_api_gateway_method.llm_chat_options.http_method
  status_code = aws_api_gateway_method_response.llm_chat_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "llm_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.llm_chatbot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.llm_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "llm_api_deployment" {
  depends_on = [
    aws_api_gateway_method.llm_chat_post,
    aws_api_gateway_method.llm_chat_options,
    aws_api_gateway_integration.llm_lambda_integration,
    aws_api_gateway_integration.llm_chat_options_integration,
    aws_api_gateway_integration_response.llm_chat_options_integration_response
  ]

  rest_api_id = aws_api_gateway_rest_api.llm_api.id
  stage_name  = "prod"
}

# Output the API Gateway URL
output "llm_api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.llm_api.id}.execute-api.us-east-1.amazonaws.com/prod/chat"
}
