terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.16"
    }
  }
}

provider "volterra" {
  timeout      = "90s"
  api_p12_file = "/opt/f5-consult.console.ves.volterra.io.api-creds.p12"
  url          = "https://f5-consult.console.ves.volterra.io/api"
}
