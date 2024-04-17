# Overview

Created by Steve Meisenzahl

This playbook will build an HA configuration between two BIGIPs utilizing roles and variable files.

For more information on roles see the document below
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html

## Requirements
Refer to the following links for the f5_modules installation
     https://clouddocs.f5.com/products/orchestration/ansible/devel/f5_modules/getting_started.html

Install f5_modules collection for ansible "https://galaxy.ansible.com/ui/repo/published/f5networks/f5_modules/"

Refer to the following links for f5os installations
    https://clouddocs.f5.com/products/orchestration/ansible/devel/f5os/F5OS-index.html

Install f5os collection for ansible "https://galaxy.ansible.com/f5networks/f5os"

Run the following command from within "/root/.ansible/collections" 
```
    ansible-galaxy collection install f5networks.f5_modules

    ansible-galaxy collection install f5networks.f5os
```
For any API calls to the rSeries F5OS layer, it's important to include the following header 
    "Content-Type application/yang-data+json" 
 
 HTTP command connection to the rSeries uses the following port;
  8888

## Configuration Items
    Note: All passwords for the remote devices are encrypted using Ansible Vault, for more information about Ansible Vault refer to the document link below.
        https://my.f5.com/manage/s/article/K64450989

    Role 1 (ha-network-active) = The purpose of this role is to set up the network that will be used for the HA interface on the Active BIGIP.
            This playbook creates the HA Self-IP on the ACTIVE BIGIP, and then configures the device connectivity options for failover and sync.
        
        This role uses the following directories and files to fulfill the build request by modifying the vars main.yml file.
                defaults = main.yml
                tasks = main.yml
                vars = main.yml
            Note: this role calls the ha1 hosts directory within the hosts file.


    Role 2 (ha-network-standby) = The purpose of this role is to set up the network that will be used for the HA interface on the Active BIGIP.
            This playbook creates the HA Self-IP on the STANDBY BIGIP, and then configures the device connectivity options for failover and sync.
        
        This role uses the following directories and files to fulfill the build request by modifying the vars main.yml file.
                defaults = main.yml
                tasks = main.yml
                vars = main.yml
            Note: this role calls the ha2 hosts directory within the hosts file.

    Role 3 (ha-setup-active) = The purpose of this role is to discover the standby device and add it to the trust.
        
        This role uses the following directories and files to fulfill the build request by modifying the vars main.yml file.
                defaults = main.yml
                tasks = main.yml
                vars = main.yml
            Note: this role calls the ha1 hosts directory within the hosts file.

    Role 4 (ha-failback-standby) = The purpose of this role is to set up the network that will be used for the HA interface on the Standby BIGIP.
             This role uses the following directories and files to fulfill the build request.
                defaults = main.yml
                tasks = main.yml
            Note: this role calls the ha2 hosts directory within the hosts file.

    Role 5 (ha-initial-sync) = The purpose of this role is to perform the initial sync from the active BIGIP1.
            This role uses the following directories and files to fulfill the build request.
                defaults = main.yml
                tasks = main.yml
            Note: this role calls the ha1 hosts directory within the hosts file.
      


Each of the above objects has its roles, find the role and expand it.  Look for the "files" directory to edit the .json file.  Once the file is edited with your environment information save the file.

Authentication will be added in the future

## Roles

As stated above, each configured object has a specific role designed to configure that object and will need to be modified for each rSeries built.

Under the roles directory, there are 7 subdirectories, see below
    defaults
    files
    handlers
    meta
    tasks
    tests
    vars

The configuration for each role will most likely differ, below is a list of roles this playbook utilizes.

    Role 1 (ha-network-active)
    Role 2 (ha-network-standby)
    Role 3 (ha-setup-active)
    Role 4 (ha-failback-standby)
    Role 5 (ha-initial-sync)

## Inventory

Under the "Inventory" directory should be the "hosts" file that has information on what remote device the playbook will run against.

In this case, the playbook is running against a remote rSeries device.

Within the "hosts" file there is a section called rSeries with the IP address of the remote device, see below for an example of this entry

    [ha1]
        x.x.x.x ansible_host=x.x.x.x private_ip=x.x.x.x

    [ha2]
        y.y.y.y ansible_host=y.y.y.y private_ip=y.y.y.y

## Usage
```
For this playbook, the passwords are encrypted with Ansible Vault, use the "--ask-vault-pass" command to log into the device

    ansible-playbook --ask-vault-pass ha-setup.yaml

    add -vvv for more verbose output when troubleshooting any issues.
```
