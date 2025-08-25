# DynamoDB Module for Voice Assistant AI
# NoSQL database for conversation state and user data

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# KMS Key for DynamoDB encryption
resource "aws_kms_key" "dynamodb" {
  description             = "KMS key for DynamoDB encryption"
  deletion_window_in_days = var.kms_key_deletion_window

  tags = var.tags
}

resource "aws_kms_alias" "dynamodb" {
  name          = "alias/${var.name_prefix}-dynamodb"
  target_key_id = aws_kms_key.dynamodb.key_id
}

# Main conversations table
resource "aws_dynamodb_table" "conversations" {
  name           = "${var.name_prefix}-conversations"
  billing_mode   = var.billing_mode
  hash_key       = "user_id"
  range_key      = "conversation_id"
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Provisioned throughput (only used if billing_mode is PROVISIONED)
  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "conversation_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "session_id"
    type = "S"
  }

  # Global Secondary Index for querying by timestamp
  global_secondary_index {
    name            = "timestamp-index"
    hash_key        = "user_id"
    range_key       = "timestamp"
    projection_type = "ALL"

    read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
    write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null
  }

  # Global Secondary Index for querying by session
  global_secondary_index {
    name            = "session-index"
    hash_key        = "session_id"
    projection_type = "ALL"

    read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
    write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null
  }

  # Server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  # TTL configuration
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = var.tags
}

# User sessions table
resource "aws_dynamodb_table" "user_sessions" {
  name         = "${var.name_prefix}-user-sessions"
  billing_mode = var.billing_mode
  hash_key     = "session_id"

  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # Global Secondary Index for querying by user
  global_secondary_index {
    name            = "user-index"
    hash_key        = "user_id"
    projection_type = "ALL"

    read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
    write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = var.tags
}

# Analytics table for storing interaction metrics
resource "aws_dynamodb_table" "analytics" {
  name         = "${var.name_prefix}-analytics"
  billing_mode = var.billing_mode
  hash_key     = "metric_type"
  range_key    = "timestamp"

  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  attribute {
    name = "metric_type"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = var.tags
}

# Auto Scaling for provisioned tables (if billing_mode is PROVISIONED)
resource "aws_appautoscaling_target" "conversations_read" {
  count = var.billing_mode == "PROVISIONED" && var.enable_autoscaling ? 1 : 0

  max_capacity       = var.autoscaling_read_max_capacity
  min_capacity       = var.autoscaling_read_min_capacity
  resource_id        = "table/${aws_dynamodb_table.conversations.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "conversations_write" {
  count = var.billing_mode == "PROVISIONED" && var.enable_autoscaling ? 1 : 0

  max_capacity       = var.autoscaling_write_max_capacity
  min_capacity       = var.autoscaling_write_min_capacity
  resource_id        = "table/${aws_dynamodb_table.conversations.name}"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "conversations_read" {
  count = var.billing_mode == "PROVISIONED" && var.enable_autoscaling ? 1 : 0

  name               = "${var.name_prefix}-conversations-read-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.conversations_read[0].resource_id
  scalable_dimension = aws_appautoscaling_target.conversations_read[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.conversations_read[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = var.autoscaling_target_value
  }
}

resource "aws_appautoscaling_policy" "conversations_write" {
  count = var.billing_mode == "PROVISIONED" && var.enable_autoscaling ? 1 : 0

  name               = "${var.name_prefix}-conversations-write-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.conversations_write[0].resource_id
  scalable_dimension = aws_appautoscaling_target.conversations_write[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.conversations_write[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = var.autoscaling_target_value
  }
}

# CloudWatch Alarms for DynamoDB
resource "aws_cloudwatch_metric_alarm" "conversations_throttles" {
  alarm_name          = "${var.name_prefix}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors DynamoDB throttles"

  dimensions = {
    TableName = aws_dynamodb_table.conversations.name
  }

  tags = var.tags
}
