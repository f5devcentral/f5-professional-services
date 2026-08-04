terraform {
  required_providers {
    volterra = {
      source = "volterraedge/volterra"
      version = "0.11.49"
    }
  }
}

provider "volterra" {
  api_p12_file     = var.api_p12_file
  url              = var.api_url
}