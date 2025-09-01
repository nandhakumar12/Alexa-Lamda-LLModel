#############################
# CI/CD Pipeline with GitHub
#############################

provider "aws" {
  region = var.region
}

#####################################
# Random suffix for unique S3 bucket
#####################################
resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "pipeline_artifacts" {
  bucket = "voice-ai-pipeline-artifacts-${random_id.suffix.hex}"
}

#####################################
# SNS Topic for Notifications
#####################################
resource "aws_sns_topic" "pipeline_notifications" {
  name = "voice-ai-pipeline-notifications"
}

#####################################
# CodeStar GitHub Connection
#####################################
resource "aws_codestarconnections_connection" "github" {
  name          = "github-connection"
  provider_type = "GitHub"
}

#####################################
# IAM Roles
#####################################
resource "aws_iam_role" "codepipeline_role" {
  name = "Voice-Ai-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      },
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      },
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:*",
          "sns:*",
          "codebuild:*",
          "codestar-connections:*",
          "lambda:*",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "codestar-connections:UseConnection"
        ]
        Resource = [
          aws_codestarconnections_connection.github.arn
        ]
      }
    ]
  })
}

#####################################
# CodeBuild Projects (example)
#####################################
resource "aws_codebuild_project" "build_project" {
  name          = "voice-ai-build"
  service_role  = aws_iam_role.codepipeline_role.arn
  build_timeout = 10

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = true

    environment_variable {
      name  = "ENVIRONMENT"
      value = var.environment
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-deploy.yml"
  }
}

#####################################
# Lambda Example (Placeholder)
#####################################
# Note: This Lambda is created as an example for the pipeline
# In a real deployment, the Lambda would be deployed by the pipeline itself
data "archive_file" "dummy_lambda" {
  type        = "zip"
  output_path = "${path.module}/dummy_lambda.zip"
  
  source {
    content  = "def handler(event, context): return {'statusCode': 200, 'body': 'Hello from Lambda'}"
    filename = "index.py"
  }
}

resource "aws_lambda_function" "backend_lambda" {
  function_name = "${var.name_prefix}-backend-lambda"
  role          = aws_iam_role.codepipeline_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  filename         = data.archive_file.dummy_lambda.output_path
  source_code_hash = data.archive_file.dummy_lambda.output_base64sha256
}

#####################################
# CodePipeline
#####################################
resource "aws_codepipeline" "voice_ai_pipeline" {
  name     = "voice-ai-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    type     = "S3"
    location = aws_s3_bucket.pipeline_artifacts.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "GitHub_Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

              configuration = {
          ConnectionArn    = aws_codestarconnections_connection.github.arn
          FullRepositoryId = "nandhakumar12/Alexa-Lamda-LLModel" # Updated with your actual repo
          BranchName       = "main"
        }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]

      configuration = {
        ProjectName = aws_codebuild_project.build_project.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "DeployLambda"
      category        = "Invoke"
      owner           = "AWS"
      provider        = "Lambda"
      version         = "1"
      input_artifacts = ["build_output"]

      configuration = {
        FunctionName = aws_lambda_function.backend_lambda.function_name
      }
    }
  }
}

#####################################
# Outputs
#####################################
output "pipeline_name" {
  description = "Name of the CodePipeline created"
  value       = aws_codepipeline.voice_ai_pipeline.name
}

output "artifact_bucket" {
  description = "S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.pipeline_artifacts.bucket
}

output "sns_topic_arn" {
  description = "SNS Topic ARN for pipeline notifications"
  value       = aws_sns_topic.pipeline_notifications.arn
}

output "codebuild_project_name" {
  description = "CodeBuild project name for build stage"
  value       = aws_codebuild_project.build_project.name
}

output "lambda_function_name" {
  description = "Deployed backend Lambda function name"
  value       = aws_lambda_function.backend_lambda.function_name
}

output "github_connection_arn" {
  description = "GitHub CodeStar Connection ARN"
  value       = aws_codestarconnections_connection.github.arn
}
