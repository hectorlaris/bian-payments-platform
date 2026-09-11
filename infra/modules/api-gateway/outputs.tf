output "api_id" {
  description = "The HTTP API id."
  value       = aws_apigatewayv2_api.this.id
}

output "api_endpoint" {
  description = "The invoke endpoint for the default stage."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "authorizer_id" {
  description = "The Cognito JWT authorizer id."
  value       = aws_apigatewayv2_authorizer.cognito.id
}
