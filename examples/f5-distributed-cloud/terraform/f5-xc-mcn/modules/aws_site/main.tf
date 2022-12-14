terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_aws_vpc_site" "aws_site" {
  name       = var.name
  namespace  = "system"
  aws_region = var.aws_region

  blocked_services {
    blocked_sevice {
      ssh = true
      dns = true
    }
  }

  aws_cred {
    name      = var.aws_cred
    namespace = "system"
  }
  vpc {
    new_vpc {
      autogenerate = true
      primary_ipv4 = var.vpc_cidr
    }
  }
  instance_type           = var.instance_type
  logs_streaming_disabled = true

  ingress_egress_gw {
    allowed_vip_port {
      use_http_https_port = true
    }
    aws_certified_hw = "aws-byol-multi-nic-voltmesh"

    az_nodes {
      aws_az_name = var.aws_az_name
      disk_size   = "80"
      inside_subnet {
        subnet_param {
          ipv4 = var.aws_inside_subnet
        }
      }
      outside_subnet {
        subnet_param {
          ipv4 = var.aws_outside_subnet
        }
      }
    }
  }
  lifecycle {
    ignore_changes = [labels]
  }
}

resource "volterra_cloud_site_labels" "labels" {
  name      = volterra_aws_vpc_site.aws_site.name
  site_type = "aws_vpc_site"
  labels = {
    siteName       = var.siteName
  }
  ignore_on_delete = true
}

resource "volterra_tf_params_action" "apply_aws_vpc" {
  site_name        = volterra_aws_vpc_site.aws_site.name
  site_kind        = "aws_vpc_site"
  action           = "apply"
  wait_for_action  = true
  ignore_on_update = true
}
