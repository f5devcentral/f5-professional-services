terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.49"
    }
  }
}

locals {
  classified_origin = [
    for value in var.origins : {
      type  = can(regex("^\\d{1,3}(\\.\\d{1,3}){3}$", value.origin)) ? "ip" : "fqdn"
      origins = value
      private = (value.site != "" || value.virtual_site != "") ? true : false
    }
  ]
  private_origin = contains(local.classified_origin[*].private,true)
}

resource "volterra_origin_pool" "f5-origin" {
  name                   = var.name
  namespace              = var.namespace
  loadbalancer_algorithm = "LB_OVERRIDE"
  endpoint_selection     = "LOCAL_PREFERRED"
  port                   = var.port
    
  # Dynamic block for public servers
  dynamic "origin_servers" {
    for_each = local.classified_origin
    content {
      dynamic "public_ip" {
        for_each = origin_servers.value.type == "ip" && origin_servers.value.private == false ? [1] : []
        content {
          ip = origin_servers.value.origins.origin
        }
      }
      dynamic "public_name" {
        for_each = origin_servers.value.type == "fqdn" && origin_servers.value.private == false ? [1] : []
        content {
          dns_name = origin_servers.value.origins.origin
        }
      }
      dynamic "private_ip" {
        for_each = origin_servers.value.type == "ip" && origin_servers.value.private == true ? [1] : []
        content {
          ip = origin_servers.value.origins.origin
          site_locator {
            dynamic site {
              for_each = origin_servers.value.origins.site != "" ? [1] : []
              content {
                namespace = "system"
                name      =  origin_servers.value.origins.site
              }
            }
            dynamic virtual_site {
              for_each = origin_servers.value.origins.virtual_site != "" ? [1] : []
              content {
                namespace = "shared"
                name      =  origin_servers.value.origins.virtual_site
              }
            }
          }
          outside_network = can(regex("outside",origin_servers.value.origins.network))
          inside_network  = can(regex("inside",origin_servers.value.origins.network))
        }
      }
      dynamic "private_name" {
        for_each = origin_servers.value.type == "fqdn" && origin_servers.value.private == true ? [1] : []
        content {
          dns_name = origin_servers.value.origins.origin
          site_locator {
            dynamic site {
              for_each = origin_servers.value.origins.site != "" ? [1] : []
              content {
                namespace = "system"
                name      =  origin_servers.value.origins.site
              }
            }
            dynamic virtual_site {
              for_each = origin_servers.value.origins.virtual_site != "" ? [1] : []
              content {
                namespace = "shared"
                name      =  origin_servers.value.origins.virtual_site
              }
            }
          }
          outside_network = can(regex("outside",origin_servers.value.origins.network))
          inside_network  = can(regex("inside",origin_servers.value.origins.network))
        }
      }
    }
  }
 
  dynamic "use_tls" {
    for_each = var.use_tls == true ? [1] : []
    content {
      tls_config {}
     }
  }
  
  no_tls = true
  upstream_conn_pool_reuse_type {
    disable_conn_pool_reuse = false
    enable_conn_pool_reuse  = true
  }

  healthcheck {
    name      = var.healthcheck
    tenant    = var.tenant
    namespace = var.namespace
  }
}