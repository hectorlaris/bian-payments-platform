terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # Remote state backend. Values are supplied at init time via -backend-config
  # (see infra/README.md), so this block stays free of environment-specific values.
  backend "s3" {
    key = "payments/dev/terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}
