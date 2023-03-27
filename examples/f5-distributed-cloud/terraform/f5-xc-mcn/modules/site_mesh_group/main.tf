terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_site_mesh_group" "site_mesh_group" {
  name        = var.name
  namespace   = "system"
  full_mesh {
    data_plane_mesh = true
  }
  virtual_site {
    name = var.virtual_site_name
    namespace = "shared"
  }
}
