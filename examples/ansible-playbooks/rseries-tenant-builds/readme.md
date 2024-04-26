# Overview

Created by Steve Meisenzahl

This playbook will build a new Tenant on a rSeries utilizing roles and JSON files.
For more information on roles see the document below
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html

## Requirements

Install f5os collection for ansible using the following link "https://galaxy.ansible.com/f5networks/f5os"

Run the following command from within "/root/.ansible/collections" 
```
    ansible-galaxy collection install f5networks.f5os
```
For any API calls to the rSeries F5OS layer, it's important to include the following header 
    "Content-Type application/yang-data+json" 
 
 HTTP command connection to the rSeries uses the following port;
  8888

## Configuration Items
    Note: All passwords for the remote devices are encrypted using Ansible Vault, for more information about Ansible Vault refer to the document link below.
        https://my.f5.com/manage/s/article/K64450989

    Role 1 (tenant-build) = The purpose of this role is to build a new tenant shell on rSeries, configuring the following objects.
            Name defined on rSeries
            Tenant Image to be used
            Tenant Management IP
            Tenant Management Gateway
            Tenant Management Subnet Mask
            Tenant vCPU
            Tenant Memory
            Tenant Vlans
            Tenant Running State
            Tenant Cryptos = Whether crypto and compression hardware offload is enabled on the tenant. F5 recommends enabling it, otherwise, crypto and compression can be processed in CPU.
        
        This role uses the following directories and files to fulfill the build request by modifying the .json files and the vars main.yml file.
                files = tenant-shell.json
                        tenant-deploy.json
                tasks = main.yml
                vars = main.yml


    Role 2 (change-passwords) = The purpose of this role is to change default passwords to corporate passwords on a new tenant, configuring the following objects.
            Admin password
            Root password

        This role uses the following directories to fulfill the password change request.
                defaults = main.yml
                tasks = main.yml

    Role 3 (tenant-initial-setup) = The purpose of this role is to complete the initial setup on a new tenant, configuring the following objects.
            Disable GUI setup
            Provision LTM and AVR
            Sets the Hostname of the device

        This role uses the following directories and files to fulfill the initial setup request by modifying the vars main.yml file.
                defaults = main.yml
                tasks = main.yml
                vars = main.yml

    Role 4 (tenant-corp-defaults) = The purpose of this role is to configure the corporate defaults on a new tenant. Under the files directory is the onboarding.py script written in Python.
             The above-called-out script file is proprietary to the client and will not be uploaded.
             Utilizing the following link, objects can be configured, for example, but not limited to;
                DNS
                NTP
                SNMP
                Authentication
                SSHD
                HTTPD
            https://clouddocs.f5.com/products/orchestration/ansible/devel/modules/module_index.html

        This role uses the following directories and files to fulfill the corporate default setup request.
                defaults = main.yml
                files = onboarding.py (this file is not uploaded and is proprietary to the client, substitute any other script file to fulfill this requirement or build using modules)
                tasks = main.yml
                vars = main.yml

    Role 5 (device-cert) = The purpose of this role is to change the device certificate utilizing script files.
            The first script file records the current device certificate and backs up the default.crt and default.key files, also while creating a .ucs
            The second script file sets the new device certificate after modifying the file with client-specific information

        This role uses the following directories and files to fulfill the corporate default setup request.
                defaults = main.yml
                files = getcert.sh
                        createnewcert.sh
                tasks = main.yml
      


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

    Role 1 (tenant-build)
    Role 2 (change-passwords)
    Role 3 (tenant-initial-setup)
    Role 4 (tenant-corp-defaults)
    Role 5 (device-cert)

## Inventory

Under the "Inventory" directory should be the "hosts" file that has information on what remote device the playbook will run against.

In this case, the playbook is running against a remote rSeries device.

Within the "hosts" file there is a section called rSeries with the IP address of the remote device, see below for an example of this entry

    [tenants]
        10.x.x.1 ansible_host=10.x.x.1 private_ip=10.x.x.1
        10.x.x.2 ansible_host=10.x.x.2 private_ip=10.x.x.2

## Usage
```
For this playbook, the passwords are encrypted with Ansible Vault, use the "--ask-vault-pass" command to log into the device

    ansible-playbook --ask-vault-pass tenant-build.yaml

    add -vvv for more verbose output when troubleshooting any issues.
