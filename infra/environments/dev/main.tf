locals {
  common_tags = {
    Project     = "payments-mvp"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

module "network" {
  source      = "../../modules/network"
  name_prefix = var.name_prefix
  vpc_cidr    = var.vpc_cidr
  tags        = local.common_tags
}

module "msk" {
  source      = "../../modules/msk"
  name_prefix = var.name_prefix
  vpc_id      = module.network.vpc_id
  vpc_cidr    = var.vpc_cidr
  subnet_ids  = module.network.private_subnet_ids
  tags        = local.common_tags
}

module "eventbridge" {
  source      = "../../modules/eventbridge"
  name_prefix = var.name_prefix
  tags        = local.common_tags
}

module "cognito" {
  source        = "../../modules/cognito"
  name_prefix   = var.name_prefix
  domain_suffix = var.cognito_domain_suffix
  aws_region    = var.aws_region
  tags          = local.common_tags
}

module "readmodel" {
  source      = "../../modules/readmodel"
  name_prefix = var.name_prefix
  tags        = local.common_tags
}

module "compute" {
  source      = "../../modules/compute"
  name_prefix = var.name_prefix
  tags        = local.common_tags
}

module "api_gateway" {
  source        = "../../modules/api-gateway"
  name_prefix   = var.name_prefix
  aws_region    = var.aws_region
  user_pool_id  = module.cognito.user_pool_id
  app_client_id = module.cognito.app_client_id
  tags          = local.common_tags
}

# Application secret placeholder (rotated out-of-band). Never store the value in code.
resource "aws_secretsmanager_secret" "app" {
  name        = "${var.name_prefix}/app"
  description = "Application secrets for the payments services."
  tags        = local.common_tags
}
