terraform {
  required_providers {
    bigip = {
      source  = "F5Networks/bigip"
      version = ">= 1.16.0"
    }
  }
}
provider "bigip" {
  address  = "x.x.x.x"
  username = "username"
  password = "password"

}

//Resource to create an ltm monitor 

resource "bigip_ltm_monitor" "monitor_terraform" {
  name   = "/Common/terraform_monitor"
  parent = "/Common/http"
}

//Resource to create a pool with the following attributes:

resource "bigip_ltm_pool" "pool" {
  name                   = var.name   //name will be defined on main.tf
  load_balancing_mode    = "round-robin"
  minimum_active_members = 1
  monitors               = [bigip_ltm_monitor.monitor_terraform.name]
  description = var.description //description will be defined on main.tf
}

