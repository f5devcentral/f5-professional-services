terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_cloud_credentials" "gcp_cc" {
  name      = var.name
  namespace = "system"

  gcp_cred_file {
    credential_file {
      clear_secret_info {
        url = "string:///${base64encode(var.gcp_secret)}"
      }
    }
  }
}
