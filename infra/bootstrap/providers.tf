terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # Bootstrap intentionally uses LOCAL state. It creates the remote backend that the
  # dev environment then uses. Commit the generated bootstrap terraform.tfstate to a
  # safe location or keep it locally; it is small and rarely changes.
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "payments-mvp"
      Purpose   = "ci-bootstrap"
      ManagedBy = "terraform"
    }
  }
}
