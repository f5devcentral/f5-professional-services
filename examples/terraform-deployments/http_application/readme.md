# Overview

This terraform code creates a sample node, pool and a http virtual server.

## How it works

The script leverages from the  bigip terraform provider https://registry.terraform.io/providers/F5Networks/bigip/latest to create resources and also use local modules to abstract the configuration and expose only certain attributes to the main.tf


## Requirements

* Install terraform locally or on the cloud:  https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

* The bigip provider uses the iControlREST API. All the resources are validated with BigIP v12.1.1 and above.

## Usage
```
 terraform plan -var-file="<input_variable_name_file>.tfvars"
 terraform apply -var-file="<input_variable_name_file>.tfvars"
 
```

## Example
```
terraform plan -var-file="input.tfvars" 
terraform apply -var-file="input.tfvars" 

```
## Output

```

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # bigip_ltm_pool_attachment.attach_node_to_pool will be created
  + resource "bigip_ltm_pool_attachment" "attach_node_to_pool" {
      + connection_limit      = (known after apply)
      + connection_rate_limit = (known after apply)
      + dynamic_ratio         = (known after apply)
      + id                    = (known after apply)
      + node                  = "/Common/Terraform_node:80"
      + pool                  = "/Common/Terraform_Pool"
      + priority_group        = (known after apply)
      + ratio                 = (known after apply)
    }

  # bigip_ltm_virtual_server.http will be created
  + resource "bigip_ltm_virtual_server" "http" {
      + default_persistence_profile    = (known after apply)
      + destination                    = "10.12.12.12"
      + fallback_persistence_profile   = (known after apply)
      + firewall_enforced_policy       = (known after apply)
      + id                             = (known after apply)
      + ip_protocol                    = "tcp"
      + mask                           = (known after apply)
      + name                           = "/Common/terraform_vs_http"
      + per_flow_request_access_policy = (known after apply)
      + pool                           = "/Common/Terraform_Pool"
      + port                           = 80
      + profiles                       = (known after apply)
      + snatpool                       = (known after apply)
      + source                         = (known after apply)
      + source_address_translation     = (known after apply)
      + source_port                    = (known after apply)
      + state                          = "enabled"
      + trafficmatching_criteria       = (known after apply)
      + translate_address              = "enabled"
      + translate_port                 = "enabled"
      + vlans_enabled                  = false
    }

  # module.nodes.bigip_ltm_node.node_test will be created
  + resource "bigip_ltm_node" "node_test" {
      + address          = "10.10.10.10"
      + connection_limit = 0
      + description      = "test_pool"
      + dynamic_ratio    = 1
      + id               = (known after apply)
      + monitor          = "/Common/icmp"
      + name             = "/Common/Terraform_node"
      + rate_limit       = "disabled"
      + ratio            = (known after apply)
      + session          = (known after apply)
      + state            = (known after apply)

      + fqdn {
          + address_family = "ipv4"
          + autopopulate   = (known after apply)
          + downinterval   = (known after apply)
          + interval       = "3000"
        }
    }

  # module.pools.bigip_ltm_monitor.monitor_terraform will be created
  + resource "bigip_ltm_monitor" "monitor_terraform" {
      + adaptive       = (known after apply)
      + adaptive_limit = (known after apply)
      + compatibility  = "enabled"
      + destination    = (known after apply)
      + id             = (known after apply)
      + interval       = (known after apply)
      + ip_dscp        = (known after apply)
      + manual_resume  = (known after apply)
      + mode           = (known after apply)
      + name           = "/Common/terraform_monitor"
      + parent         = "/Common/http"
      + reverse        = (known after apply)
      + send           = (known after apply)
      + time_until_up  = (known after apply)
      + timeout        = (known after apply)
      + transparent    = (known after apply)
      + up_interval    = (known after apply)
    }

  # module.pools.bigip_ltm_pool.pool will be created
  + resource "bigip_ltm_pool" "pool" {
      + allow_nat              = (known after apply)
      + allow_snat             = (known after apply)
      + description            = "terraform_pool"
      + id                     = (known after apply)
      + load_balancing_mode    = "round-robin"
      + minimum_active_members = 1
      + monitors               = [
          + "/Common/terraform_monitor",
        ]
      + name                   = "/Common/Terraform_Pool"
      + reselect_tries         = (known after apply)
      + service_down_action    = (known after apply)
      + slow_ramp_time         = (known after apply)
    }

Plan: 5 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + ip_node         = "10.10.10.10"
  + name_node       = "/Common/Terraform_node"
  + name_pool       = "/Common/Terraform_Pool"
  + virtual_adrress = "10.12.12.12"
  + virtual_name    = "/Common/terraform_vs_http"

```



