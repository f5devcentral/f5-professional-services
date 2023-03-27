terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_virtual_site" "virtual_site" {
  name      = var.name
  namespace = var.namespace
  site_selector {
    expressions = var.expressions
  }
  site_type = var.site_type
}
