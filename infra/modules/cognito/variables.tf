variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "domain_suffix" {
  description = "Suffix to make the hosted UI domain globally unique."
  type        = string
}

variable "resource_server_identifier" {
  description = "The resource server identifier (e.g. https://api.example-bank.com)."
  type        = string
  default     = "https://api.example-bank.com"
}

variable "scopes" {
  description = "OAuth2 scopes exposed by the resource server."
  type        = list(string)
  default     = ["payments.initiate", "payments.read", "payments.write", "payments.execute"]
}

variable "aws_region" {
  description = "AWS region (used to build the token endpoint URL)."
  type        = string
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
