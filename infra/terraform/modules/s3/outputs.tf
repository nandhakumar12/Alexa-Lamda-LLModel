# Voice Assistant AI - S3 Module Outputs

# Files bucket outputs
output "files_bucket_name" {
  description = "Name of the files S3 bucket"
  value       = aws_s3_bucket.files.bucket
}

output "files_bucket_arn" {
  description = "ARN of the files S3 bucket"
  value       = aws_s3_bucket.files.arn
}

output "files_bucket_domain_name" {
  description = "Domain name of the files S3 bucket"
  value       = aws_s3_bucket.files.bucket_domain_name
}

output "files_bucket_regional_domain_name" {
  description = "Regional domain name of the files S3 bucket"
  value       = aws_s3_bucket.files.bucket_regional_domain_name
}

# Web bucket outputs
output "web_bucket_name" {
  description = "Name of the web S3 bucket"
  value       = aws_s3_bucket.web.bucket
}

output "web_bucket_arn" {
  description = "ARN of the web S3 bucket"
  value       = aws_s3_bucket.web.arn
}

output "web_bucket_domain_name" {
  description = "Domain name of the web S3 bucket"
  value       = aws_s3_bucket.web.bucket_domain_name
}

output "web_bucket_regional_domain_name" {
  description = "Regional domain name of the web S3 bucket"
  value       = aws_s3_bucket.web.bucket_regional_domain_name
}

output "web_bucket_website_endpoint" {
  description = "Website endpoint of the web S3 bucket"
  value       = aws_s3_bucket_website_configuration.web.website_endpoint
}

output "web_bucket_website_domain" {
  description = "Website domain of the web S3 bucket"
  value       = aws_s3_bucket_website_configuration.web.website_domain
}

# Legacy outputs for backward compatibility
output "bucket_name" {
  description = "Name of the files S3 bucket (legacy)"
  value       = aws_s3_bucket.files.bucket
}

output "bucket_arn" {
  description = "ARN of the files S3 bucket (legacy)"
  value       = aws_s3_bucket.files.arn
}

output "bucket_domain_name" {
  description = "Domain name of the files S3 bucket (legacy)"
  value       = aws_s3_bucket.files.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the files S3 bucket (legacy)"
  value       = aws_s3_bucket.files.bucket_regional_domain_name
}
