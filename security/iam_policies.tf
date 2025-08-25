# IAM Policies for Voice Assistant AI
# Security configurations with least privilege access

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

# Variables
variable "project_name" {
  description = "Project name"
  type        = string
  default     = "voice-assistant-ai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.name
}

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${local.name_prefix}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = local.region
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# Lambda Basic Execution Policy
resource "aws_iam_policy" "lambda_basic_execution" {
  name        = "${local.name_prefix}-lambda-basic-execution"
  description = "Basic execution policy for Lambda functions"

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
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-*:*"
        ]
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# DynamoDB Access Policy
resource "aws_iam_policy" "dynamodb_access" {
  name        = "${local.name_prefix}-dynamodb-access"
  description = "DynamoDB access policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          "arn:aws:dynamodb:${local.region}:${local.account_id}:table/${local.name_prefix}-*",
          "arn:aws:dynamodb:${local.region}:${local.account_id}:table/${local.name_prefix}-*/index/*"
        ]
        Condition = {
          StringEquals = {
            "dynamodb:LeadingKeys" = ["$${aws:userid}"]
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# S3 Access Policy
resource "aws_iam_policy" "s3_access" {
  name        = "${local.name_prefix}-s3-access"
  description = "S3 access policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-*/*"
        ]
        Condition = {
          StringLike = {
            "s3:x-amz-server-side-encryption" = "AES256"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-*"
        ]
        Condition = {
          StringLike = {
            "s3:prefix" = ["audio/*", "uploads/*"]
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# Lex Access Policy
resource "aws_iam_policy" "lex_access" {
  name        = "${local.name_prefix}-lex-access"
  description = "Amazon Lex access policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lex:PostContent",
          "lex:PostText",
          "lex:RecognizeText",
          "lex:RecognizeUtterance"
        ]
        Resource = [
          "arn:aws:lex:${local.region}:${local.account_id}:bot/${local.name_prefix}-*"
        ]
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# KMS Access Policy
resource "aws_iam_policy" "kms_access" {
  name        = "${local.name_prefix}-kms-access"
  description = "KMS access policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = [
          "arn:aws:kms:${local.region}:${local.account_id}:key/*"
        ]
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "dynamodb.${local.region}.amazonaws.com",
              "s3.${local.region}.amazonaws.com",
              "logs.${local.region}.amazonaws.com"
            ]
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# X-Ray Tracing Policy
resource "aws_iam_policy" "xray_tracing" {
  name        = "${local.name_prefix}-xray-tracing"
  description = "X-Ray tracing policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# CloudWatch Metrics Policy
resource "aws_iam_policy" "cloudwatch_metrics" {
  name        = "${local.name_prefix}-cloudwatch-metrics"
  description = "CloudWatch metrics policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "VoiceAssistantAI"
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# Secrets Manager Access Policy
resource "aws_iam_policy" "secrets_manager_access" {
  name        = "${local.name_prefix}-secrets-manager-access"
  description = "Secrets Manager access policy for Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${var.project_name}/*"
        ]
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# VPC Access Policy (if Lambda functions are in VPC)
resource "aws_iam_policy" "vpc_access" {
  name        = "${local.name_prefix}-vpc-access"
  description = "VPC access policy for Lambda functions"

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

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# Attach policies to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_basic_execution.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_role_policy_attachment" "lex_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lex_access.arn
}

resource "aws_iam_role_policy_attachment" "kms_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.kms_access.arn
}

resource "aws_iam_role_policy_attachment" "xray_tracing" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.xray_tracing.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_metrics" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.cloudwatch_metrics.arn
}

resource "aws_iam_role_policy_attachment" "secrets_manager_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

# API Gateway Execution Role
resource "aws_iam_role" "api_gateway_execution_role" {
  name = "${local.name_prefix}-api-gateway-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# API Gateway CloudWatch Logs Policy
resource "aws_iam_policy" "api_gateway_cloudwatch_logs" {
  name        = "${local.name_prefix}-api-gateway-cloudwatch-logs"
  description = "CloudWatch logs policy for API Gateway"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/apigateway/${local.name_prefix}*"
        ]
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch_logs" {
  role       = aws_iam_role.api_gateway_execution_role.name
  policy_arn = aws_iam_policy.api_gateway_cloudwatch_logs.arn
}

# Lex Bot Service Role
resource "aws_iam_role" "lex_bot_role" {
  name = "${local.name_prefix}-lex-bot-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lexv2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# Attach AWS managed policy for Lex
resource "aws_iam_role_policy_attachment" "lex_bot_policy" {
  role       = aws_iam_role.lex_bot_role.name
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/LexBotPolicy"
}

# CodePipeline Service Role
resource "aws_iam_role" "codepipeline_role" {
  name = "${local.name_prefix}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

# CodePipeline Policy
resource "aws_iam_policy" "codepipeline_policy" {
  name        = "${local.name_prefix}-codepipeline-policy"
  description = "Policy for CodePipeline service role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketVersioning",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-pipeline-artifacts",
          "arn:aws:s3:::${local.name_prefix}-pipeline-artifacts/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ]
        Resource = [
          "arn:aws:codebuild:${local.region}:${local.account_id}:project/${local.name_prefix}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [
          "arn:aws:sns:${local.region}:${local.account_id}:${local.name_prefix}-*"
        ]
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "security"
  }
}

resource "aws_iam_role_policy_attachment" "codepipeline_policy" {
  role       = aws_iam_role.codepipeline_role.name
  policy_arn = aws_iam_policy.codepipeline_policy.arn
}

# Outputs
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "api_gateway_execution_role_arn" {
  description = "ARN of the API Gateway execution role"
  value       = aws_iam_role.api_gateway_execution_role.arn
}

output "lex_bot_role_arn" {
  description = "ARN of the Lex bot role"
  value       = aws_iam_role.lex_bot_role.arn
}

output "codepipeline_role_arn" {
  description = "ARN of the CodePipeline role"
  value       = aws_iam_role.codepipeline_role.arn
}
