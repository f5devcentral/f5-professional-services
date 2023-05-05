terraform {
  required_providers {
    bigip = {
      source  = "F5Networks/bigip"
      version = ">= 1.16.0"
    }
  }
}
provider "bigip" {
  address  = "10.154.86.118"
  username = "admin"
  password = "karce123"

}

//Resource to create a node with the following attributes:

resource "bigip_ltm_node" "node_test" {
  name             = var.name     // name will be defined on main.tf
  address          = var.address  // address will be defined on main.tf
  connection_limit = "0"
  dynamic_ratio    = "1"
  description = var.description
  monitor          = "/Common/icmp"
  rate_limit       = "disabled"
  fqdn {
    address_family = "ipv4"
    interval       = "3000"
  }
}

