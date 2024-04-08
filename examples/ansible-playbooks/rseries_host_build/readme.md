# Overview

Create by Steve Meisenzahl

This playbook will build the base configuration for a rSeries utilizing roles and JSON files.
For more information on roles see the document below.
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html

## Requirements

Install f5os collection for ansible using the following link "https://galaxy.ansible.com/f5networks/f5os"

Run the following command from within "/root/.ansible/collections" 
```
    ansible-galaxy collection install f5networks.f5os
```
For any API calls to the rSeries F5OS layer it's important to include the following header 
    "Content-Type application/yang-data+json" 
 
 HTTP command connnection to the rSeries uses the following port;
  8888

## Configuration Items

The following objects are configured with this playbook

    Hostname 
    Banner 
    Banner MOTD
    DNS
    NTP
    Remote Logging
    Portgroup Speeds
    Vlans
    Interfaces to Vlans
    LAGs
    Interfaces to LAGs
    LACP on LAGs
    SNMP Allow List
    SNMP Location
    SNMP Community
    SNMP Security View
    SNMP Traps
    SNMP Target

Each of the above objects have thier own roles, find the role and expand it.  Look for the "files" directory to edit the .json file.  Once the file is edited with your environment information save the file.

Authentication will be added in the future

## Roles

As stated above, each configured object has a specific role designed to configure that object and will need to be modied for each rSeries built.

Under the roles directory there are 7 sub directories, see below
    defaults
    files
    handlers
    meta
    tasks
    tests
    vars

The configuration for each role will most likely differ, but for the most part, within this playbook, objects will be configured from the files and tasks directories.

See an example of the .json file below that needs to be modified;

    "files" = Under this directory there is a .json file called from a task, this file will need to be modified for the environement or rSeries being built
        {
            "openconfig-system:system": {
                    "config": {
                        "hostname": "R4600-R85-S4",
                        "login-banner": "*************** THIS SYSTEM IS A SECURE AND PRIVATE DEVICE. IF YOU HAVE CONNECTED TO THIS DEVICE BY MISTAKE, PLEASE DISCONNECT NOW. ***************",
                        "motd-banner": "*************** F5 private system please disconnect. ***************"
                }
            }
        }


    "tasks" = Contain the configuration commands that will be sent to the remote rSeries to configure specific objects, see an example task below.

        ---
          - name: Modify Hostname and Banners
            uri:
              url: https://{{ private_ip }}:8888/restconf/data/
              user: "{{ ansible_admin }}"
              password: "{{ ansible_ssh_pass }}"
              method: PATCH
              headers:
                Content-Type: application/yang-data+json
                Accept: application/yang-data+json
              force_basic_auth: yes
              force: yes
              status_code: 200,204
              return_content: true
              validate_certs: no
              body_format: json
              body: "{{ lookup('ansible.builtin.file','files/banner.json') }}"
            register: Banner

## Inventory

Under the "Inventory" directory should be the "hosts" file that has information on what remote device the playbook will run against.

In this case the playbook is running against a remote rSeries device.

Within the "hosts" file there is section called rSeries with the IP address of the remote device, see below for an example of this entry

    [rseries]
        10.x.x.x ansible_host=10.x.x.x private_ip=10.x.x.x

## Usage
```
For this playbook, the passwords are encrypted with Ansible Vault, use the "--ask-vault-pass" command to log into the device

    ansible-playbook --ask-vault-pass rseries-base-build.yaml

    add -vvv for a more verbose output when troubleshooting any issues.
```

