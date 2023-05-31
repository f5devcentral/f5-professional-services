terraform {
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "1.18.0"
    }

    bigip = {
      source  = "F5Networks/bigip"
      version = ">= 1.16.0"
    }

  }
}


provider "restapi" {
  uri                   = "https://10.154.86.15:8888/"
  write_returns_object  = true
  insecure              = true
  create_returns_object = true
  debug                 = true
  headers = {
    Authorization  = var.token
    "Content-Type" = "application/yang-data+json"
  }

  create_method  = "POST"
  update_method  = "PUT"
  destroy_method = "DELETE"


}


provider "bigip" {
  address  = var.bigip_address
  username = var.admin_user
  password = var.admin_password
}


