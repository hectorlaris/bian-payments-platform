output "github_actions_role_arn" {
  description = "Set this as the GitHub secret AWS_ROLE_ARN."
  value       = aws_iam_role.deploy.arn
}

output "state_bucket" {
  description = "S3 bucket for Terraform remote state (use in -backend-config)."
  value       = aws_s3_bucket.state.id
}

output "lock_table" {
  description = "DynamoDB table for state locking (use in -backend-config)."
  value       = aws_dynamodb_table.locks.name
}

output "aws_region" {
  description = "Region for the backend and deploys."
  value       = var.aws_region
}

output "account_id" {
  description = "The AWS account id the bootstrap ran in."
  value       = data.aws_caller_identity.current.account_id
}
