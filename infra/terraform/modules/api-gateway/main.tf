# API Gateway Module for Voice Assistant AI
# RESTful API with Lambda integration and Cognito authorization

# API Gateway REST API
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.name_prefix}-api"
  description = "Voice Assistant AI API Gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  binary_media_types = [
    "audio/*",
    "image/*",
    "application/octet-stream"
  ]

  tags = var.tags
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  depends_on = [
    aws_api_gateway_method.chatbot_post,
    aws_api_gateway_method.auth_post,
    aws_api_gateway_method.health_get,
    aws_api_gateway_method.alexa_post
  ]

  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.chatbot.id,
      aws_api_gateway_method.chatbot_post.id,
      aws_api_gateway_integration.chatbot_lambda.id,
      aws_api_gateway_resource.auth.id,
      aws_api_gateway_method.auth_post.id,
      aws_api_gateway_integration.auth_lambda.id,
      aws_api_gateway_resource.health.id,
      aws_api_gateway_method.health_get.id,
      aws_api_gateway_integration.health_lambda.id,
      aws_api_gateway_resource.alexa.id,
      aws_api_gateway_method.alexa_post.id,
      aws_api_gateway_integration.alexa_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      responseTime   = "$context.responseTime"
      error          = "$context.error.message"
      integrationError = "$context.integration.error"
    })
  }

  xray_tracing_enabled = var.enable_xray_tracing

  tags = var.tags
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.name_prefix}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# API Gateway Method Settings
resource "aws_api_gateway_method_settings" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled    = true
    logging_level      = "INFO"
    data_trace_enabled = var.environment != "prod"
    throttling_rate_limit  = var.throttle_rate_limit
    throttling_burst_limit = var.throttle_burst_limit
  }
}

# CORS Configuration
resource "aws_api_gateway_gateway_response" "cors" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_4XX"

  response_templates = {
    "application/json" = jsonencode({
      message = "$context.error.messageString"
    })
  }

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}

resource "aws_api_gateway_gateway_response" "cors_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_5XX"

  response_templates = {
    "application/json" = jsonencode({
      message = "$context.error.messageString"
    })
  }

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}

# Cognito Authorizer
resource "aws_api_gateway_authorizer" "cognito" {
  name          = "${var.name_prefix}-cognito-authorizer"
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.main.id
  provider_arns = [var.cognito_user_pool_arn]
}

# API Resources and Methods

# /chatbot resource
resource "aws_api_gateway_resource" "chatbot" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "chatbot"
}

resource "aws_api_gateway_method" "chatbot_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chatbot.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_validator_id = aws_api_gateway_request_validator.main.id
}

resource "aws_api_gateway_method" "chatbot_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chatbot.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# /auth resource
resource "aws_api_gateway_resource" "auth" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "auth"
}

resource "aws_api_gateway_method" "auth_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth.id
  http_method   = "POST"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.main.id
}

resource "aws_api_gateway_method" "auth_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# /health resource
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

# /alexa resource (for Alexa Skills Kit)
resource "aws_api_gateway_resource" "alexa" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "alexa"
}

resource "aws_api_gateway_method" "alexa_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.alexa.id
  http_method   = "POST"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.main.id
}

# Request Validator
resource "aws_api_gateway_request_validator" "main" {
  name                        = "${var.name_prefix}-validator"
  rest_api_id                 = aws_api_gateway_rest_api.main.id
  validate_request_body       = true
  validate_request_parameters = true
}

# Lambda Integrations
resource "aws_api_gateway_integration" "chatbot_lambda" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chatbot.id
  http_method = aws_api_gateway_method.chatbot_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.chatbot_lambda_arn}/invocations"
}

resource "aws_api_gateway_integration" "auth_lambda" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth.id
  http_method = aws_api_gateway_method.auth_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.auth_lambda_arn}/invocations"
}

resource "aws_api_gateway_integration" "health_lambda" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.monitoring_lambda_arn}/invocations"
}

resource "aws_api_gateway_integration" "alexa_lambda" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.alexa.id
  http_method = aws_api_gateway_method.alexa_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.chatbot_lambda_arn}/invocations"
}

# CORS Integration Responses
resource "aws_api_gateway_integration" "chatbot_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chatbot.id
  http_method = aws_api_gateway_method.chatbot_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

resource "aws_api_gateway_integration" "auth_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth.id
  http_method = aws_api_gateway_method.auth_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

# Method Responses for CORS
resource "aws_api_gateway_method_response" "chatbot_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chatbot.id
  http_method = aws_api_gateway_method.chatbot_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_method_response" "auth_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth.id
  http_method = aws_api_gateway_method.auth_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# Integration Responses for CORS
resource "aws_api_gateway_integration_response" "chatbot_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chatbot.id
  http_method = aws_api_gateway_method.chatbot_options.http_method
  status_code = aws_api_gateway_method_response.chatbot_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_integration_response" "auth_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth.id
  http_method = aws_api_gateway_method.auth_options.http_method
  status_code = aws_api_gateway_method_response.auth_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
