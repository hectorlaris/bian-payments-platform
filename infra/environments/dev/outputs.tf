output "vpc_id" {
  description = "The VPC id."
  value       = module.network.vpc_id
}

output "msk_bootstrap_brokers_tls" {
  description = "MSK TLS bootstrap brokers."
  value       = module.msk.bootstrap_brokers_tls
}

output "event_bus_name" {
  description = "The integration event bus name."
  value       = module.eventbridge.event_bus_name
}

output "cognito_user_pool_id" {
  description = "The Cognito user pool id."
  value       = module.cognito.user_pool_id
}

output "cognito_token_endpoint" {
  description = "The OAuth2 token endpoint."
  value       = module.cognito.token_endpoint
}

output "read_model_table" {
  description = "The DynamoDB read-model table name."
  value       = module.readmodel.table_name
}

output "api_endpoint" {
  description = "The API Gateway invoke endpoint."
  value       = module.api_gateway.api_endpoint
}
