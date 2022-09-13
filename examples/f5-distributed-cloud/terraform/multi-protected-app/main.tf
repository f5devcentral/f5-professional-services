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

locals {
  baseobj_csv = csvdecode(file("${path.module}/input.csv"))
  baseobj = { for app in local.baseobj_csv : app.base_name => app }
}

data "local_file" "cert" {
  filename = "${path.module}/certs/acme.crt"
}
data "local_file" "key" {
  filename = "${path.module}/certs/acme.key"
}

resource "volterra_app_firewall" "af" {
  name        = format("%s-app-firewall", var.base)
  description = format("App Firewall in blocking mode for %s", var.base)
  namespace   = "shared"

  allow_all_response_codes = true
  default_anonymization = true
  use_default_blocking_page = true
  default_bot_setting = true
  default_detection_settings = true
  blocking = true
}

resource "volterra_healthcheck" "origin-heath-check" {
  for_each = local.baseobj
  name                   = format("%s-health-check", each.value.base_name)
  namespace              = var.namespace
  http_health_check {
    use_origin_server_name = true
    path                   = "/"
  }
  healthy_threshold   = 3
  interval            = 15
  timeout             = 3
  unhealthy_threshold = 1
}

resource "volterra_origin_pool" "f5-origin" {
  for_each = local.baseobj
  name                   = format("%s-f5-origin", each.value.base_name)
  namespace              = var.namespace
  description            = format("Origin pool pointing to our origin!")
  loadbalancer_algorithm = "LB_OVERRIDE"
  endpoint_selection     = "LOCAL_PREFERRED"
  
  origin_servers {
    
    dynamic "public_name" {
      for_each = length(regexall("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$",each.value.origin_server)) > 0 ? [] : [1]
      content {
        dns_name  = each.value.origin_server
      }
    }
    dynamic "public_ip" {
      for_each = length(regexall("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$",each.value.origin_server)) > 0 ? [1] : []
      content {
        ip  = each.value.origin_server
      }
    }

  }

  port               = each.value.origin_server_port
  no_tls             = each.value.origin_server_no_tls
  healthcheck {
    name = volterra_healthcheck.origin-heath-check[each.key].name
  }
}

resource "volterra_http_loadbalancer" "app-lb" {
  for_each = local.baseobj
  name                            = format("%s-lb", each.value.base_name)
  namespace                       = var.namespace
  description                     = format("HTTPS loadbalancer object for %s origin server", var.base)
  domains                         = [each.value.fqdn]
  advertise_on_public_default_vip = each.value.auto_cert == "true" ? true : false
  do_not_advertise                = each.value.auto_cert == "true" ? false : true
  default_route_pools {
    pool {
      name      = volterra_origin_pool.f5-origin[each.key].name
      namespace = var.namespace
    }
  }
  dynamic "https_auto_cert" {
    for_each = each.value.auto_cert == "true" ? [1] : []

    content {
      add_hsts              = false
      http_redirect         = true
      enable_path_normalize = true
    }
  }

  dynamic "https" {
    for_each = each.value.auto_cert == "true" ? [] : [1]

    content {
      add_hsts              = false
      http_redirect         = true
      enable_path_normalize = true
      tls_parameters {
        no_mtls = true
        tls_certificates {
          certificate_url = format("string:///%s", data.local_file.cert.content_base64)
          private_key {
            clear_secret_info {
              url = format("string:///%s", data.local_file.key.content_base64)
            }
          }
        }
      }
    }
  }

  multi_lb_app = true
  app_firewall {
    name      = volterra_app_firewall.af.name
    namespace = volterra_app_firewall.af.namespace
  }
  disable_rate_limit              = true
  service_policies_from_namespace = true
  no_challenge                    = true
  add_location                    = true
}
