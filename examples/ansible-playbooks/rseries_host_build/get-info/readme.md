This directory holds all the "get" yaml files to retreive information, ie, DNS, NTP, Vlans, Interfaces, LAGs, etc.
# Overview

These playbooks will retrieve specific configuration objects for an rSeries when run individually, they can also be combined into one playbook.

## Requirements

Install f5os collection for ansible using the following link "https://galaxy.ansible.com/f5networks/f5os"

Run the following command from within "/root/.ansible/collections" 
```
ansible-galaxy collection install f5networks.f5os
```
For any API calls to the rSeries F5OS layer it is important to include the following header 
 "Content-Type application/yang-data+json" 
 
 HTTP command connnection to the rSeries uses the following port;
  8888

## Usage
```
ansible-playbook -vvv <playbook-name>.yaml
```
