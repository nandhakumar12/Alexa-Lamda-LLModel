# Voice Assistant AI - S3 Module
# S3 buckets for file storage and static website hosting

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

# Random suffix for unique bucket naming
locals {
  bucket_suffix = var.bucket_suffix
}

# S3 Bucket for file storage
resource "aws_s3_bucket" "files" {
  bucket = "${var.name_prefix}-files-${local.bucket_suffix}"

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-files-${local.bucket_suffix}"
    Purpose     = "File Storage"
    Component   = "storage"
  })
}

# S3 Bucket for static website hosting
resource "aws_s3_bucket" "web" {
  bucket = "${var.name_prefix}-web-${local.bucket_suffix}"

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-web-${local.bucket_suffix}"
    Purpose     = "Static Website Hosting"
    Component   = "frontend"
  })
}

# Bucket versioning for files bucket
resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# Bucket versioning for web bucket
resource "aws_s3_bucket_versioning" "web" {
  bucket = aws_s3_bucket.web.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption for files bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Server-side encryption for web bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access for files bucket (private)
resource "aws_s3_bucket_public_access_block" "files" {
  bucket = aws_s3_bucket.files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Allow public access for web bucket (for static hosting)
resource "aws_s3_bucket_public_access_block" "web" {
  bucket = aws_s3_bucket.web.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Static website hosting configuration
resource "aws_s3_bucket_website_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Bucket policy for public read access to web bucket
resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.web.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.web]
}

# CORS configuration for web bucket
resource "aws_s3_bucket_cors_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = var.cors_allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# CORS configuration for files bucket
resource "aws_s3_bucket_cors_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = var.cors_allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Lifecycle configuration for files bucket
resource "aws_s3_bucket_lifecycle_configuration" "files" {
  count  = var.lifecycle_enabled ? 1 : 0
  bucket = aws_s3_bucket.files.id

  rule {
    id     = "audio-files-lifecycle"
    status = "Enabled"

    filter {
      prefix = "audio/"
    }

    transition {
      days          = var.transition_to_ia_days
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = var.transition_to_glacier_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.expiration_days
    }
  }

  rule {
    id     = "uploads-cleanup"
    status = "Enabled"

    filter {
      prefix = "uploads/"
    }

    expiration {
      days = 7
    }
  }
}

# Notification configuration for files bucket
resource "aws_s3_bucket_notification" "files" {
  bucket = aws_s3_bucket.files.id

  # Add Lambda function notifications if needed
  # lambda_function {
  #   lambda_function_arn = var.lambda_function_arn
  #   events              = ["s3:ObjectCreated:*"]
  #   filter_prefix       = "uploads/"
  # }
}
