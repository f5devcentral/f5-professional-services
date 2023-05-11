# Overview

This terraform deployment create the basic configuration on a F5OS tenant and an HTTPS application using AS3, DO and terraform.
The code can be used on any BIG-IP with 13.1 and later, but is not specific for a F5OS tenant

## How it works

This deployment leverages from the terraform bigip provider https://registry.terraform.io/providers/F5Networks/bigip/latest and uses the F5 Automation Tool Chain(ATC).
The script automates L1-L3 on-boarding for BIG-IP using DO and then configure L4-L7 Application Services configurations using AS3

## Requirements

* You must have an existing BIG-IP tenant device with a management IP address.
* The BIG-IP must be running version 13.1 or later.
* You must have an existing user account with the Administrator role. If you are using 13.1.x, the BIG-IP contains an admin user by default. If you are using 14.x, you must reset the admin password before installing BIG-IP Declarative Onboarding. See If using BIG-IP 14.0 or later for instructions.

### Notes and Tips

For more details on Prerequisites and Requirements visit: https://clouddocs.f5.com/products/extensions/f5-declarative-onboarding/latest/prereqs.html#prerequisites-and-requirements

