terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_gcp_vpc_site" "gcp_site" {
  name       = var.name
  namespace  = "system"
  gcp_region = var.gcp_region

  cloud_credentials {
    name      = var.gcp_cred
    namespace = "system"
  }

  blocked_services {
    blocked_sevice {
      ssh = true
      dns = true
    }
  }
  instance_type           = "n1-standard-4"
  logs_streaming_disabled = true

  ingress_gw {
    gcp_certified_hw = "gcp-byol-voltmesh"
    gcp_zone_names   = ["us-east1-b"]
    local_network {
      new_network_autogenerate {
        autogenerate = true
      }
    }
    local_subnet {
      new_subnet {
        primary_ipv4 = var.primary_ipv4
        subnet_name  = var.subnet_name
      }
    }
    node_number = "1"
  }
  lifecycle {
    ignore_changes = [labels]
  }
}

resource "volterra_cloud_site_labels" "labels" {
  name      = volterra_gcp_vpc_site.gcp_site.name
  site_type = "gcp_vpc_site"
  labels = {
    siteName       = var.siteName
  }
  ignore_on_delete = true
}

resource "volterra_tf_params_action" "apply_gcp_site" {
  site_name        = volterra_gcp_vpc_site.gcp_site.name
  site_kind        = "gcp_vpc_site"
  action           = "apply"
  wait_for_action  = true
  ignore_on_update = true
}