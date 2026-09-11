variable "aws_region" {
  description = "AWS region for the state backend and OIDC role."
  type        = string
  default     = "us-east-1"
}

variable "github_owner" {
  description = "GitHub account or org that owns the repository."
  type        = string
  default     = "hectorlaris"
}

variable "github_repo" {
  description = "GitHub repository name (without owner)."
  type        = string
  default     = "bian-payments-platform"
}

variable "state_bucket_name" {
  description = "Globally unique S3 bucket name for Terraform remote state (include an account-specific suffix)."
  type        = string
}

variable "lock_table_name" {
  description = "DynamoDB table name for Terraform state locking."
  type        = string
  default     = "payments-tf-locks"
}

variable "deploy_role_name" {
  description = "Name of the IAM role GitHub Actions will assume via OIDC."
  type        = string
  default     = "payments-github-actions-deploy"
}

variable "allowed_environments" {
  description = "GitHub deployment environments allowed to assume the role (plus pull_request for plan)."
  type        = list(string)
  default     = ["dev", "dev-apply"]
}
