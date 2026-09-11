data "aws_caller_identity" "current" {}

locals {
  # GitHub's OIDC subject claims. Restrict role assumption to this repository and,
  # for deploys, to the specific deployment environments; pull_request is allowed so
  # the `plan` job can run OIDC on PRs.
  repo = "${var.github_owner}/${var.github_repo}"
  allowed_subs = concat(
    [for env in var.allowed_environments : "repo:${local.repo}:environment:${env}"],
    ["repo:${local.repo}:pull_request"],
  )
}

# --- GitHub OIDC identity provider -------------------------------------------------
# Create once per AWS account. If it already exists, import it instead of recreating:
#   terraform import aws_iam_openid_connect_provider.github \
#     arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]
  # Note: AWS no longer validates the thumbprint for the GitHub OIDC endpoint, but the
  # argument is still required by the API. The placeholder above is accepted.
}

# --- IAM role assumed by GitHub Actions --------------------------------------------
data "aws_iam_policy_document" "trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.allowed_subs
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = var.deploy_role_name
  assume_role_policy = data.aws_iam_policy_document.trust.json
  description        = "Role assumed by GitHub Actions (OIDC) to plan/apply the payments dev environment."
}

# Deploy permissions. This is intentionally broad enough to manage the dev stack
# (VPC, MSK, EventBridge, Cognito, DynamoDB, ECS, API Gateway, IAM, Secrets Manager,
# logs) plus read/write the Terraform state backend. Tighten per your security review.
data "aws_iam_policy_document" "deploy" {
  statement {
    sid    = "TerraformStateBackend"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = [
      aws_s3_bucket.state.arn,
      "${aws_s3_bucket.state.arn}/*",
    ]
  }

  statement {
    sid    = "TerraformStateLock"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]
    resources = [aws_dynamodb_table.locks.arn]
  }

  statement {
    sid    = "DevStackManagement"
    effect = "Allow"
    actions = [
      "ec2:*",
      "kafka:*",
      "events:*",
      "cognito-idp:*",
      "dynamodb:*",
      "ecs:*",
      "apigateway:*",
      "logs:*",
      "secretsmanager:*",
      "kms:*",
      "iam:GetRole",
      "iam:PassRole",
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:ListRolePolicies",
      "iam:ListAttachedRolePolicies",
      "iam:TagRole",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "${var.deploy_role_name}-policy"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}

# --- Remote state backend: S3 bucket + DynamoDB lock table -------------------------
resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "locks" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
