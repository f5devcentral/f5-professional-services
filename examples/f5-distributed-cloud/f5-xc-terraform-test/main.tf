locals {
  app-firewall-name = format("%s-app-fw-mod", var.base)
  health-check-name = format("%s-health-check-mod", var.base)
  origin-name       = format("%s-module-op", var.base)
  http-lb-name      = format("%s-lb-mod", var.base)
  new_signature_staging_period_by_env_map = {
    "prod" = 20
    "qaf"  = 10
    "dev"  = 4
  }
}

module "app-firewall" {
  source    = "./modules/f5-xc-app-firewall"
  name      = local.app-firewall-name
  namespace = var.namespace
}

module "health-check" {
  source    = "./modules/f5-xc-health-check"
  name      = local.health-check-name
  namespace = var.namespace
}

module "origin" {
  source      = "./modules/f5-xc-origin-pool"
  name        = local.origin-name
  tenant      = var.tenant
  namespace   = var.namespace
  origins     = var.origin_servers
  healthcheck = module.health-check.name
  use_tls     = var.use_tls
  port        = var.origin_pool_port
}

module "http-lb" {
  source               = "./modules/f5-xc-http-lb"
  name                 = local.http-lb-name
  tenant               = var.tenant
  namespace            = var.namespace
  origin_pool          = module.origin.name
  app_firewall_name    = module.app-firewall.name
  domains              = var.domains
  enable_api_discovery = false
  waf_policy           = var.waf_policy
  service_policy       = var.service_policy
}