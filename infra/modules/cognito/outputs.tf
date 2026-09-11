output "user_pool_id" {
  description = "The Cognito user pool id."
  value       = aws_cognito_user_pool.this.id
}

output "user_pool_arn" {
  description = "The Cognito user pool ARN (for API Gateway authorizer)."
  value       = aws_cognito_user_pool.this.arn
}

output "app_client_id" {
  description = "The machine-to-machine app client id."
  value       = aws_cognito_user_pool_client.m2m.id
}

output "token_endpoint" {
  description = "The OAuth2 token endpoint."
  value       = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${var.aws_region}.amazoncognito.com/oauth2/token"
}
