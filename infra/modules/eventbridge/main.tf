# EventBridge module: an integration event bus, a rule matching payment integration
# events, and a CloudWatch Logs target standing in for a notification consumer.

resource "aws_cloudwatch_event_bus" "this" {
  name = "${var.name_prefix}-integration"
  tags = var.tags
}

resource "aws_cloudwatch_event_rule" "payment_status" {
  name           = "${var.name_prefix}-payment-status"
  event_bus_name = aws_cloudwatch_event_bus.this.name
  description    = "Route payment completion/failure integration events."

  event_pattern = jsonencode({
    source        = ["payments.order"]
    "detail-type" = ["PaymentCompleted", "PaymentFailed"]
  })

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "notifications" {
  name              = "/payments/${var.name_prefix}/notifications"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_event_target" "notifications" {
  rule           = aws_cloudwatch_event_rule.payment_status.name
  event_bus_name = aws_cloudwatch_event_bus.this.name
  arn            = aws_cloudwatch_log_group.notifications.arn
}
