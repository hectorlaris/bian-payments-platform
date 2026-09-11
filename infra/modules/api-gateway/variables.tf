variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "aws_region" {
  description = "AWS region (used to build the Cognito issuer URL)."
  type        = string
}

variable "user_pool_id" {
  description = "Cognito user pool id for the JWT authorizer issuer."
  type        = string
}

variable "app_client_id" {
  description = "Cognito app client id used as the JWT audience."
  type        = string
}

variable "throttling_burst_limit" {
  description = "API Gateway burst limit."
  type        = number
  default     = 50
}

variable "throttling_rate_limit" {
  description = "API Gateway steady-state rate limit (req/s)."
  type        = number
  default     = 100
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
