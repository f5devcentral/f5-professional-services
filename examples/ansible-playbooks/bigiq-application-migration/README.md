# BIGIQ Application Migration via Ansible

## Table of Contents
- [Overview](#overview)
- [Environment Setup](#environment-setup)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [License](#license)

## Overview
This project provides an Ansible playbook for migrating Application Services from one BIG-IP device to another using BIG-IQ. 

It automates the migration process, eliminating the need for manual intervention. The playbook leverages the [f5devcentral.bigiq_migrate_apps](https://galaxy.ansible.com/ui/standalone/roles/f5devcentral/bigiq_migrate_apps/documentation/) Ansible role and dynamically handles existing application services in BIG-IQ.

Key features:
- Prevent manual intervention by dynamically managing variables and configurations.
- Consistent and scalable migration process.
- Leverages F5's Ansible Imperative Collection for control of F5 devices.

## Enviroment

1. Create a *Python3* virtual environment:

```bash
python3 -m venv myansible
```

2. Activate the virtual environment:

```bash
source myansible/bin/activate
```

3. Install *Ansible*:

```bash
pip install ansible
```

4. Install **F5 Ansible Imperative Collection**:

```bash
ansible-galaxy collection install f5networks.f5_modules
```

## How It Works

The migration process involves the following files:

1. **bigiq.yaml**:  
   - The main playbook used to orchestrate the migration.

2. **ntarget.yaml**:  
   - Reads the file `Files/ips.csv` to identify the new target BIG-IP device for the application.

3. **migrate.yaml**:  
   - Dynamically calls the `bigiq_migrate_apps` role with the necessary variables.

#### Key Snippet from `migrate.yaml`:
```yaml
- name: Include f5devcentral.bigiq_migrate_apps role
  tags:
    - iqrole  
  include_role:
    name: f5devcentral.bigiq_migrate_apps  
  vars:
    dir_as3: ~/tmp  # Directory to store temporary AS3 definitions for migration
    device_address: "{{ target_address }}"  # Source BIG-IP device where the application(s) currently exist
    tenant_to_migrate: "{{ iqtenant }}"  # Source tenant (partition) to be migrated from the source BIG-IP
    new_device_address: "{{ new_tgt_addr }}"  # Target BIG-IP device for the migrated application(s)
    new_tenant_name: "{{ iqtenant }}_new"  # Target tenant (partition) on the target BIG-IP; must differ from "tenant_to_migrate"
    new_bigiq_app_name: "{{ move_to_app }}"  # BIG-IQ application name where all associated services will be moved or consolidated
  when: target_address != 'undefined'  
```
## Usage
Running the playbook
```bash
ansible-playbook playbooks/bigiq.yaml
```
Running playbook example
```yaml
TASK [f5devcentral.bigiq_move_app_dashboard : Fail if you're running the role against a DCD device] **************************************************************************************************************************************
skipping: [bigiq]

TASK [f5devcentral.bigiq_move_app_dashboard : Check if system is setup] ******************************************************************************************************************************************************************
ok: [bigiq]

TASK [f5devcentral.bigiq_move_app_dashboard : Stop if the system is not setup] ***********************************************************************************************************************************************************
skipping: [bigiq]

TASK [f5devcentral.bigiq_move_app_dashboard : Show all App Services to add into the Application in BIG-IQ dashboard] *********************************************************************************************************************
ok: [bigiq] => (item=[{'name': 'BIG IQ App'}, {'name': 'App_IQ_new_VsService'}]) => {
    "msg": "Application Service App_IQ_new_VsService belonging to BIG IQ App "
}
ok: [bigiq] => (item=[{'name': 'BIG IQ App'}, {'name': 'App_IQ_2_new_Service'}]) => {
    "msg": "Application Service App_IQ_2_new_Service belonging to BIG IQ App "
}
TASK [f5devcentral.bigiq_move_app_dashboard : Show Application & Application Service] ****************************************************************************************************************************************************
ok: [bigiq] => {
    "msg": "Application Service App_IQ_2_new_Service belonging to BIG IQ App"
}

TASK [f5devcentral.bigiq_move_app_dashboard : Get Config set for Application Service] ****************************************************************************************************************************************************
ok: [bigiq]

TASK [f5devcentral.bigiq_move_app_dashboard : Get the selfLink of the Application Service] ***********************************************************************************************************************************************
ok: [bigiq]

TASK [f5devcentral.bigiq_move_app_dashboard : Move Application Service to Application defined in BIG-IQ dashboard] ***********************************************************************************************************************
ok: [bigiq]

TASK [f5devcentral.bigiq_migrate_apps : Get app services details to cleanup] *************************************************************************************************************************************************************
skipping: [bigiq]

TASK [f5devcentral.bigiq_migrate_apps : Cleanup old tenant AS3 apps when device is reachable] ********************************************************************************************************************************************
skipping: [bigiq]

TASK [f5devcentral.bigiq_migrate_apps : Cleanup old tenant AS3 apps when device is NOT reachable] ****************************************************************************************************************************************
skipping: [bigiq] => (item=App_IQ_2_new_Service) 
skipping: [bigiq]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************
bigiq                      : ok=174  changed=18   unreachable=0    failed=0    skipped=60   rescued=0    ignored=0  
```
