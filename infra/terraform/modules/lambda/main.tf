# Lambda Module for Voice Assistant AI
# Serverless functions for chatbot, authentication, and monitoring

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# KMS Key for Lambda encryption
resource "aws_kms_key" "lambda" {
  description             = "KMS key for Lambda function encryption"
  deletion_window_in_days = var.kms_key_deletion_window

  tags = var.tags
}

resource "aws_kms_alias" "lambda" {
  name          = "alias/${var.name_prefix}-lambda"
  target_key_id = aws_kms_key.lambda.key_id
}

# IAM Role for Lambda execution
resource "aws_iam_role" "lambda_execution" {
  name = "${var.name_prefix}-lambda-execution-role"

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

  tags = var.tags
}

# IAM Policy for Lambda execution
resource "aws_iam_policy" "lambda_execution" {
  name        = "${var.name_prefix}-lambda-execution-policy"
  description = "IAM policy for Lambda execution"

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
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::${var.s3_bucket_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "lex:PostContent",
          "lex:PostText",
          "lex:RecognizeText",
          "lex:RecognizeUtterance"
        ]
        Resource = "arn:aws:lex:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:bot/${var.lex_bot_id}"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.lambda.arn
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

# VPC Policy (if VPC is configured)
resource "aws_iam_policy" "lambda_vpc" {
  count = length(var.vpc_subnet_ids) > 0 ? 1 : 0

  name        = "${var.name_prefix}-lambda-vpc-policy"
  description = "IAM policy for Lambda VPC access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

# Attach policies to role
resource "aws_iam_role_policy_attachment" "lambda_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_execution.arn
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  count = length(var.vpc_subnet_ids) > 0 ? 1 : 0

  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_vpc[0].arn
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "chatbot" {
  name              = "/aws/lambda/${var.name_prefix}-chatbot"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.lambda.arn

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "auth" {
  name              = "/aws/lambda/${var.name_prefix}-auth"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.lambda.arn

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "monitoring" {
  name              = "/aws/lambda/${var.name_prefix}-monitoring"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.lambda.arn

  tags = var.tags
}

# Lambda Functions

# Chatbot Handler Lambda
resource "aws_lambda_function" "chatbot" {
  function_name = "${var.name_prefix}-chatbot"
  role         = aws_iam_role.lambda_execution.arn
  handler      = "handler.lambda_handler"
  runtime      = var.lambda_runtime
  timeout      = var.lambda_timeout
  memory_size  = var.lambda_memory_size

  filename         = "${path.module}/../../lambda_functions/chatbot_handler/chatbot_handler.zip"
  source_code_hash = fileexists("${path.module}/../../lambda_functions/chatbot_handler/chatbot_handler.zip") ? filebase64sha256("${path.module}/../../lambda_functions/chatbot_handler/chatbot_handler.zip") : null

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      S3_BUCKET_NAME     = var.s3_bucket_name
      LEX_BOT_ID         = var.lex_bot_id
      ENVIRONMENT        = var.environment
      LOG_LEVEL          = var.environment == "prod" ? "INFO" : "DEBUG"
    }
  }

  dynamic "vpc_config" {
    for_each = length(var.vpc_subnet_ids) > 0 ? [1] : []
    content {
      subnet_ids         = var.vpc_subnet_ids
      security_group_ids = var.vpc_security_group_ids
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  reserved_concurrent_executions = var.lambda_reserved_concurrency

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution,
    aws_cloudwatch_log_group.chatbot
  ]

  tags = var.tags
}

# Auth Handler Lambda
resource "aws_lambda_function" "auth" {
  function_name = "${var.name_prefix}-auth"
  role         = aws_iam_role.lambda_execution.arn
  handler      = "handler.lambda_handler"
  runtime      = var.lambda_runtime
  timeout      = var.lambda_timeout
  memory_size  = var.lambda_memory_size

  filename         = "${path.module}/../../lambda_functions/auth_handler/auth_handler.zip"
  source_code_hash = fileexists("${path.module}/../../lambda_functions/auth_handler/auth_handler.zip") ? filebase64sha256("${path.module}/../../lambda_functions/auth_handler/auth_handler.zip") : null

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ENVIRONMENT        = var.environment
      LOG_LEVEL          = var.environment == "prod" ? "INFO" : "DEBUG"
    }
  }

  dynamic "vpc_config" {
    for_each = length(var.vpc_subnet_ids) > 0 ? [1] : []
    content {
      subnet_ids         = var.vpc_subnet_ids
      security_group_ids = var.vpc_security_group_ids
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  reserved_concurrent_executions = var.lambda_reserved_concurrency

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution,
    aws_cloudwatch_log_group.auth
  ]

  tags = var.tags
}

# Monitoring Handler Lambda
resource "aws_lambda_function" "monitoring" {
  function_name = "${var.name_prefix}-monitoring"
  role         = aws_iam_role.lambda_execution.arn
  handler      = "handler.lambda_handler"
  runtime      = var.lambda_runtime
  timeout      = var.lambda_timeout
  memory_size  = var.lambda_memory_size

  filename         = "${path.module}/../../lambda_functions/monitoring_handler/monitoring_handler.zip"
  source_code_hash = fileexists("${path.module}/../../lambda_functions/monitoring_handler/monitoring_handler.zip") ? filebase64sha256("${path.module}/../../lambda_functions/monitoring_handler/monitoring_handler.zip") : null

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ENVIRONMENT        = var.environment
      LOG_LEVEL          = var.environment == "prod" ? "INFO" : "DEBUG"
    }
  }

  dynamic "vpc_config" {
    for_each = length(var.vpc_subnet_ids) > 0 ? [1] : []
    content {
      subnet_ids         = var.vpc_subnet_ids
      security_group_ids = var.vpc_security_group_ids
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  reserved_concurrent_executions = var.lambda_reserved_concurrency

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution,
    aws_cloudwatch_log_group.monitoring
  ]

  tags = var.tags
}
