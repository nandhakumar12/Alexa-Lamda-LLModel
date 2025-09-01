output "pipeline_name" {
  description = "Name of the CodePipeline created"
  value       = aws_codepipeline.main.name
}

output "pipeline_arn" {
  description = "ARN of the CodePipeline created"
  value       = aws_codepipeline.main.arn
}

output "artifact_bucket" {
  description = "S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.pipeline_artifacts.bucket
}

output "artifact_bucket_arn" {
  description = "ARN of the S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.pipeline_artifacts.arn
}

output "sns_topic_arn" {
  description = "SNS Topic ARN for pipeline notifications"
  value       = aws_sns_topic.pipeline_notifications.arn
}

output "github_connection_arn" {
  description = "GitHub CodeStar Connection ARN"
  value       = aws_codestarconnections_connection.github.arn
}

output "github_connection_id" {
  description = "GitHub CodeStar Connection ID"
  value       = aws_codestarconnections_connection.github.id
}

output "codebuild_projects" {
  description = "Names of all CodeBuild projects created"
  value = {
    test_and_lint    = aws_codebuild_project.test_and_lint.name
    security_scan    = aws_codebuild_project.security_scan.name
    build_and_package = aws_codebuild_project.build_and_package.name
    deploy_dev       = aws_codebuild_project.deploy_dev.name
    deploy_staging   = aws_codebuild_project.deploy_staging.name
    deploy_prod      = aws_codebuild_project.deploy_prod.name
  }
}

output "codepipeline_role_arn" {
  description = "ARN of the CodePipeline IAM role"
  value       = aws_iam_role.codepipeline_role.arn
}

output "codebuild_role_arn" {
  description = "ARN of the CodeBuild IAM role"
  value       = aws_iam_role.codebuild_role.arn
}
