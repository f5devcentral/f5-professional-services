terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = ">=0.11.25"
    }
  }
}

provider "volterra" {
  timeout      = "90s"
  api_p12_file = var.api_cred
  url          = var.api_url
}

# This module runs the blindfold.sh shell script and generate a stdout output
module "shell_blindfold" {
  source  = "Invicton-Labs/shell-data/external"
  command_unix = "./scripts/blindfold.sh ${var.lb_cert} ${var.lb_key}"
  fail_on_stderr = true
}

locals {
  description = "Used to store the output of the blindfold.sh script"
  blindfoldb64=sensitive(split(" ",module.shell_blindfold.stdout))
}
