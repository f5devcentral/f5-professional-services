terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.49"
    }
  }
}

resource "volterra_http_loadbalancer" "app-lb" {
  name                            = var.name
  namespace                       = var.namespace
  domains                         = var.domains
  advertise_on_public_default_vip = var.advertise
  service_policies_from_namespace = var.service_policy == null ? true : false
  enable_malicious_user_detection = true
  default_sensitive_data_policy   = true
  disable_api_definition          = true
  disable_api_testing             = true
  disable_api_discovery           = true
  disable_malware_protection      = true
  disable_rate_limit              = true
  disable_threat_mesh             = true
  disable_trust_client_ip_headers = true
  no_challenge                    = true
  user_id_client_ip               = true
  round_robin                     = true

  waf_exclusion {
    waf_exclusion_inline_rules {}
  }

  default_route_pools {
    pool {
      name      = var.origin_pool
      tenant    = var.tenant
      namespace = var.namespace
    }
  }

  dynamic active_service_policies {
    for_each = var.service_policy != null ? ["this"] : []
    content {
      dynamic policies {
        for_each = var.service_policy
        content {
          name      = policies.value.name
          namespace = policies.value.namespace
        }
      } 
    }
  }

  #http {
  #  dns_volterra_managed = true
  #  port_ranges = "80"
  #}

  https_auto_cert {
    http_redirect           = true
    port                    = 443
    add_hsts                = true
    connection_idle_timeout = 60000
    enable_path_normalize   = true
    no_mtls                 = true
    default_header          = true
    non_default_loadbalancer = true
    coalescing_options {
      default_coalescing            = true
    }
    tls_config {
      default_security = true
    }
     http_protocol_options {
        http_protocol_enable_v2_only = true
     }
  }
  
  dynamic "app_firewall" {
    for_each = var.waf_policy ? ["this"] : []
    content {
      name      = var.app_firewall_name
      tenant    = var.tenant
      namespace = var.namespace
    }
  }
  
  dynamic "enable_api_discovery" {
    for_each = var.enable_api_discovery == true ? [1] : []
    content {
      enable_learn_from_redirect_traffic = true
    }
  }
  
  lifecycle {
    ignore_changes = [ 
      labels,
      l7_ddos_protection
    ]
  }
}
