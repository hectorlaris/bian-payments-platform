output "event_bus_name" {
  description = "The integration event bus name."
  value       = aws_cloudwatch_event_bus.this.name
}

output "event_bus_arn" {
  description = "The integration event bus ARN."
  value       = aws_cloudwatch_event_bus.this.arn
}

output "rule_arn" {
  description = "The payment-status rule ARN."
  value       = aws_cloudwatch_event_rule.payment_status.arn
}
