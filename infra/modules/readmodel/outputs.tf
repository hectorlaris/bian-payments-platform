output "table_name" {
  description = "The DynamoDB read-model table name."
  value       = aws_dynamodb_table.payment_status.name
}

output "table_arn" {
  description = "The DynamoDB read-model table ARN."
  value       = aws_dynamodb_table.payment_status.arn
}
