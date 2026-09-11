# Cognito module: user pool, resource server with payment scopes, and an app client
# using the client-credentials flow (machine-to-machine), matching the OpenAPI contracts.

resource "aws_cognito_user_pool" "this" {
  name = "${var.name_prefix}-pool"
  tags = var.tags
}

resource "aws_cognito_user_pool_domain" "this" {
  domain       = "${var.name_prefix}-${var.domain_suffix}"
  user_pool_id = aws_cognito_user_pool.this.id
}

resource "aws_cognito_resource_server" "payments" {
  identifier   = var.resource_server_identifier
  name         = "${var.name_prefix}-payments"
  user_pool_id = aws_cognito_user_pool.this.id

  dynamic "scope" {
    for_each = var.scopes
    content {
      scope_name        = scope.value
      scope_description = "Payments scope ${scope.value}"
    }
  }
}

resource "aws_cognito_user_pool_client" "m2m" {
  name         = "${var.name_prefix}-m2m"
  user_pool_id = aws_cognito_user_pool.this.id

  generate_secret                      = true
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes = [
    for s in var.scopes : "${var.resource_server_identifier}/${s}"
  ]

  depends_on = [aws_cognito_resource_server.payments]
}
