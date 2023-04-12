# Overview

This playbook will build the base configuration on an rSeries utilizing JSON files. 

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

The following is configured with this playbook, Hostname, Banner, MOTD, DNS, NTP, Remote Logging, Portgroup Speeds, Vlans, Interfaces to Vlans, LAGs, Interfaces to LAGs, LACP on LAGs, SNMP 
Allow List, SNMP Location, SNMP Community, SNMP Security View, SNMP Traps, SNMP Target.

## Usage
```
ansible-playbook -vvv rseries-base-build.yaml
```
