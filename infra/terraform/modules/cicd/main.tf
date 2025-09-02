terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# S3 Bucket for Pipeline Artifacts
resource "aws_s3_bucket" "pipeline_artifacts" {
  bucket = "${var.name_prefix}-pipeline-artifacts-${var.suffix}"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Policy for Pipeline Artifacts
resource "aws_s3_bucket_policy" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCodePipelineAccess"
        Effect    = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.codepipeline_role.arn,
            aws_iam_role.codebuild_role.arn
          ]
        }
        Action = [
          "s3:GetBucketVersioning",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.pipeline_artifacts.arn,
          "${aws_s3_bucket.pipeline_artifacts.arn}/*"
        ]
      }
    ]
  })
}

# CodeBuild Service Role
resource "aws_iam_role" "codebuild_role" {
  name = "${var.name_prefix}-codebuild-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "codebuild_policy" {
  role = aws_iam_role.codebuild_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:GetObject",
          "s3:GetObjectVersion", 
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetBucketVersioning",
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:ListFunctions",
          "apigateway:*",
          "dynamodb:*",
          "cognito-idp:*",
          "lex:*",
          "polly:*",
          "bedrock:*",
          "secretsmanager:GetSecretValue",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "cloudformation:*",
          "iam:PassRole",
          "iam:GetRole",
          "iam:CreateRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "cloudfront:CreateInvalidation",
          "cloudfront:GetDistribution",
          "cloudfront:ListDistributions"
        ]
        Resource = "*"
      }
    ]
  })
}

# CodeBuild Projects
resource "aws_codebuild_project" "test_and_lint" {
  name        = "${var.name_prefix}-test-lint"
  description = "Test and lint code for voice assistant"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ENVIRONMENT"
      value = var.environment
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-test.yml"
  }

  tags = var.tags
}

resource "aws_codebuild_project" "security_scan" {
  name        = "${var.name_prefix}-security-scan"
  description = "Security scanning for voice assistant"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-security.yml"
  }

  tags = var.tags
}

resource "aws_codebuild_project" "build_and_package" {
  name        = "${var.name_prefix}-build-package"
  description = "Build and package voice assistant components"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ENVIRONMENT"
      value = var.environment
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec.yml"
  }

  tags = var.tags
}

resource "aws_codebuild_project" "deploy_dev" {
  name        = "${var.name_prefix}-deploy-dev"
  description = "Deploy to development environment"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ENVIRONMENT"
      value = "dev"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-deploy.yml"
  }

  tags = var.tags
}

resource "aws_codebuild_project" "deploy_staging" {
  name        = "${var.name_prefix}-deploy-staging"
  description = "Deploy to staging environment"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ENVIRONMENT"
      value = "staging"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-deploy.yml"
  }

  tags = var.tags
}

resource "aws_codebuild_project" "deploy_prod" {
  name        = "${var.name_prefix}-deploy-prod"
  description = "Deploy to production environment"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ENVIRONMENT"
      value = "prod"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-deploy.yml"
  }

  tags = var.tags
}

# CodePipeline Service Role
resource "aws_iam_role" "codepipeline_role" {
  name = "${var.name_prefix}-codepipeline-role"
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
  tags = var.tags
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  role = aws_iam_role.codepipeline_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketVersioning",
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild",
          "codecommit:CancelUploadArchive",
          "codecommit:GetBranch",
          "codecommit:GetCommit",
          "codecommit:GetRepository",
          "codecommit:ListBranches",
          "codecommit:ListRepositories",
          "codecommit:PutFile",
          "codecommit:GetUploadArchiveStatus",
          "codecommit:UploadArchive",
          "codedeploy:CreateDeployment",
          "codedeploy:GetApplication",
          "codedeploy:GetApplicationRevision",
          "codedeploy:GetDeployment",
          "codedeploy:GetDeploymentConfig",
          "codedeploy:RegisterApplicationRevision",
          "sns:Publish",
          "codestar-connections:UseConnection"
        ]
        Resource = "*"
      }
    ]
  })
}

# SNS Topic for Pipeline Notifications
resource "aws_sns_topic" "pipeline_notifications" {
  name = "${var.name_prefix}-pipeline-notifications"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_notification" {
  count     = var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.pipeline_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# CodeStar Connection for GitHub
resource "aws_codestarconnections_connection" "github" {
  name          = "voice-ai-github-connection"
  provider_type = "GitHub"
  tags          = var.tags
}

# CodePipeline
resource "aws_codepipeline" "main" {
  name     = "${var.name_prefix}-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.pipeline_artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn        = aws_codestarconnections_connection.github.arn
        FullRepositoryId     = "nandhakumar12/Alexa-Lamda-LLModel"
        BranchName           = "main"
        DetectChanges        = true
      }
    }
  }

  stage {
    name = "Test"

    action {
      name             = "TestAndLint"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["test_output"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.test_and_lint.name
      }
    }

    action {
      name             = "SecurityScan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["security_output"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.security_scan.name
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "BuildAndPackage"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.build_and_package.name
      }
    }
  }

  stage {
    name = "DeployDev"

    action {
      name            = "DeployToDev"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output", "build_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.deploy_dev.name
      }
    }
  }

  stage {
    name = "DeployStaging"

    action {
      name            = "DeployToStaging"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output", "build_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.deploy_staging.name
      }
    }
  }

  dynamic "stage" {
    for_each = var.enable_manual_approval ? [1] : []
    content {
      name = "ManualApproval"

      action {
        name    = "ManualApprovalForProd"
        category = "Approval"
        owner   = "AWS"
        provider = "Manual"
        version = "1"

        configuration = {
          NotificationArn = aws_sns_topic.pipeline_notifications.arn
          CustomData      = "Please review and approve deployment to production"
        }
      }
    }
  }

  stage {
    name = "DeployProd"

    action {
      name            = "DeployToProduction"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output", "build_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.deploy_prod.name
      }
    }
  }

  tags = var.tags
}
