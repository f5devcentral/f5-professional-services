terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.8"
    }
  }
}
resource "volterra_virtual_network" "global_network" {
  name                      = var.global_network_name
  namespace                 = var.namespace
  global_network            = true
  site_local_inside_network = false
//  site_local_network        = false
}
