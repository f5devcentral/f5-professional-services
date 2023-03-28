terraform {
  required_version = ">= 0.12.9, != 0.13.0"
        
  required_providers {
    volterra = {
      source = "volterraedge/volterra"
      version = ">=0.0.6"
    }
  }
}

provider "volterra" {
  api_cert = var.api_cert
  api_key = var.api_key
  url   = var.api_url
}

# This module runs the blindfold.sh shell script and generate a stdout output
module "shell_blindfold" {
  source  = "Invicton-Labs/shell-data/external"
  command_unix = "./scripts/blindfold.sh ${var.lb_cert} ${var.lb_key}"
  fail_on_stderr = true
  environment = {
    VES_P12_PASSWORD = "${var.VES_PASSWORD}"
  }
}

locals {
  description = "Used to store the output of the blindfold.sh script"
  blindfoldb64=sensitive(split(" ",module.shell_blindfold.stdout))
}
