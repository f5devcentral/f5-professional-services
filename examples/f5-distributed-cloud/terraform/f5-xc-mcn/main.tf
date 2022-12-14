module "aws_cc" {
  source         = "./modules/aws_credentials"
  name           = format("%s-aws-cc-tf", var.name)
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
}

module "azure_cc" {
  source           = "./modules/azure_credentials"
  name             = format("%s-az-cc-tf", var.name)
  client_id        = var.client_id
  subscription_id  = var.subscription_id
  tenant_id        = var.tenant_id
  azure_secret_key = var.azure_secret_key
}

module "gcp_cc" {
  source     = "./modules/gcp_credentials"
  name       = format("%s-gcp-cc-tf", var.name)
  gcp_secret = var.gcp_secret
}

module "virtual_site" {
  source    = "./modules/virtual_site"
  name      = format("%s-vsite-full-mesh", var.name)
  namespace = var.namespace
  expressions = ["mcn in (siteName)"]
  site_type   = "CUSTOMER_EDGE"
}

module "site_mesh_group" {
  source            = "./modules/site_mesh_group"
  name              = format("%s-site-mesh-group", var.name)
  namespace         = var.namespace
  virtual_site_name = module.virtual_site.name
  depends_on        = [module.virtual_site]
}

module "aws_site" {
  source             = "./modules/aws_site"
  name               = format("%s-amz-tf-%d", var.name, count.index)
  aws_region         = "us-west-2"
  instance_type      = "t3.xlarge"
  siteName           = "mcn"
  aws_cred           = module.aws_cc.aws_creds_name
  aws_inside_subnet  = format("10.%s.1.0/24", count.index)
  aws_outside_subnet = format("10.%s.2.0/24", count.index)
  total_nodes        = 1
  aws_az_name        = "us-west-2a"
  vpc_cidr           = format("10.%s.0.0/16", count.index)
  count              = 1
  depends_on         = [module.aws_cc]
}

module "azure_site" {
  source            = "./modules/azure_site"
  name              = format("%s-az-tf-%d", var.name, count.index)
  az_region         = "uksouth"
  siteName          = "mcn"
  az_cred           = module.azure_cc.az_creds_name
  az_inside_subnet  = format("172.%s.1.0/24", count.index)
  az_outside_subnet = format("172.%s.2.0/24", count.index)
  az_rg_name        = format("%s-az-rg-tf", var.name)
  vnet_cidr         = format("172.%s.0.0/16", count.index)
  vnet_name         = format("%s-vnet-tf", var.name)
  count             = 1
  depends_on        = [module.azure_cc]
}

module "gcp_site" {
  source            = "./modules/gcp_site"
  name              = format("%s-gcp-tf-%d", var.name, count.index)
  gcp_region        = "us-east1"
  siteName          = "mcn"
  gcp_cred          = module.gcp_cc.gcp_creds_name
  primary_ipv4      = format("192.%s.1.0/24", count.index)
  subnet_name       = format("%s-subnet-%d", var.name, count.index)
  count             = 1
  depends_on        = [module.gcp_cc]
}