# Read model module: a DynamoDB table for the CQRS payment status projection.

resource "aws_dynamodb_table" "payment_status" {
  name         = "${var.name_prefix}-payment-status"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "paymentId"

  attribute {
    name = "paymentId"
    type = "S"
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  server_side_encryption {
    enabled = true
  }

  tags = var.tags
}
