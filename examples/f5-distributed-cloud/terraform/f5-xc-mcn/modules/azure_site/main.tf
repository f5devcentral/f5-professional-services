terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_azure_vnet_site" "azure_site" {
  name      = var.name
  namespace = "system"

  blocked_services {
    blocked_sevice {
      ssh = true
      dns = true
    }
  }

  azure_cred {
    name      = var.az_cred
    namespace = "system"
  }
  vnet {
    new_vnet {
      name         = var.vnet_name
      primary_ipv4 = var.vnet_cidr
    }
  }
  logs_streaming_disabled = true
  azure_region            = var.az_region
  resource_group          = var.az_rg_name
  disk_size               = "80"
  machine_type            = "Standard_D3_v2"
  ingress_egress_gw {
    azure_certified_hw       = "azure-byol-multi-nic-voltmesh"
    no_global_network        = true
    no_outside_static_routes = true
    no_inside_static_routes  = false
    no_network_policy        = true
    no_forward_proxy         = false
    forward_proxy_allow_all  = true

    az_nodes {
      azure_az  = "1"
      disk_size = "80"
      outside_subnet {
        subnet_param {
          ipv4 = var.az_outside_subnet
        }
      }
      inside_subnet {
        subnet_param {
          ipv4 = var.az_inside_subnet
        }
      }
    }
  }
  lifecycle {
    ignore_changes = [labels]
  }
}
resource "volterra_cloud_site_labels" "labels" {
  name      = volterra_azure_vnet_site.azure_site.name
  site_type = "azure_vnet_site"
  labels = {
    siteName       = var.siteName
  }
  ignore_on_delete = true
}
resource "volterra_tf_params_action" "apply_azure_vnet" {
  site_name        = volterra_azure_vnet_site.azure_site.name
  site_kind        = "azure_vnet_site"
  action           = "apply"
  wait_for_action  = true
  ignore_on_update = true
}
