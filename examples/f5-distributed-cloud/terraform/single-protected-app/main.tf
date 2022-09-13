terraform {
  required_providers {
    volterra = {
      source = "volterraedge/volterra"
      version = "0.11.12"
    }
  }
}

provider "volterra" {
  api_p12_file     = var.api_p12_file
  url              = var.api_url
}

resource "volterra_healthcheck" "origin-heath-check" {
  name                   = format("%s-health-check", var.base)
  namespace              = var.namespace
  http_health_check {
    use_origin_server_name = true
    path                   = "/"
  }
  healthy_threshold   = 2
  interval            = 5
  timeout             = 1
  unhealthy_threshold = 5
}

resource "volterra_origin_pool" "f5-origin" {
  name                   = format("%s-f5-origin", var.base)
  namespace              = var.namespace
  description            = format("Origin pool pointing to our origin!")
  loadbalancer_algorithm = "LB_OVERRIDE"
  endpoint_selection     = "LOCAL_PREFERRED"
  origin_servers {
    public_name {
      dns_name  = "public.lab.f5demos.com"
    }
  }
  port               = 80
  no_tls             = true
  healthcheck {
    name = volterra_healthcheck.origin-heath-check.name
  }
}

resource "volterra_app_firewall" "af" {
  name        = format("%s-app-firewall", var.base)
  description = format("App Firewall in blocking mode for %s", var.base)
  namespace   = var.namespace

  allow_all_response_codes = true
  default_anonymization = true
  use_default_blocking_page = true
  default_bot_setting = true
  default_detection_settings = true
  blocking = true
}

resource "volterra_http_loadbalancer" "app-lb" {
  name                            = format("%s-lb", var.base)
  namespace                       = var.namespace
  description                     = format("HTTPS loadbalancer object for %s origin server", var.base)
  domains                         = [format("demo-app.%s", var.domain)]
  advertise_on_public_default_vip = true
  default_route_pools {
    pool {
      name      = volterra_origin_pool.f5-origin.name
      namespace = var.namespace
    }
  }
  https_auto_cert {
    add_hsts              = false
    http_redirect         = true
    no_mtls               = true
    enable_path_normalize = true
  }
  multi_lb_app = true
  app_firewall {
    name      = volterra_app_firewall.af.name
    namespace = var.namespace
  }
  disable_rate_limit              = true
  service_policies_from_namespace = true
  no_challenge                    = true
  add_location                    = true
}
