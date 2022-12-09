terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

resource "volterra_cloud_credentials" "azure_cc" {
  name      = var.name
  namespace = "system"

  azure_client_secret {
    client_id       = var.client_id
    subscription_id = var.subscription_id
    tenant_id       = var.tenant_id

    client_secret {
      clear_secret_info {
        url = "string:///${base64encode(var.azure_secret_key)}"
      }
    }
  }
}
