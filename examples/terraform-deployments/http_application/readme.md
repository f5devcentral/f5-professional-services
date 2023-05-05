# Overview

This terraform code creates a node, pool and a http virtual server.
It uses local modules to expose only certain attributes that can be modified on the input.tfvars file.

## Requirements

Install terraform locally or on the cloud: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

The bigip provider uses the iControlREST API. All the resources are validated with BigIP v12.1.1 and above.

## Usage

terraform apply -var-file="input.tfvars"



