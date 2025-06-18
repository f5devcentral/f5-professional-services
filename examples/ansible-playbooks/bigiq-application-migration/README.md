# BIGIQ Application Migration via Ansible

## Table of Contents
- [Overview](#overview)
- [Environment Setup](#environment-setup)
- [How It Works](#how-it-works)
- [CSV File Recommendation](#csv-file-recommendation)
- [Usage](#usage)
- [Best Practices](#best-practices)
- [License](#license)

## Overview
This project provides a comprehensive Ansible-based solution for migrating application services from one BIG-IP device to another via BIG-IQ. It not only handles the migration but also ensures that all application service roles associated with the old services are reassigned to the new services 

The playbooks in this repository utilize the following key roles:
- [f5devcentral.bigiq_migrate_apps](https://galaxy.ansible.com/ui/standalone/roles/f5devcentral/bigiq_migrate_apps/documentation/) 
- [f5devcentral.bigiq_apps_rbac](https://galaxy.ansible.com/ui/standalone/roles/f5devcentral/bigiq_apps_rbac/documentation/)
   

Key features:
- Automates the migration process to minimize manual intervention
- Dynamically manages variables and configurations for seamless migration.
- Ensures consistent and scalable migrations across applications and environments.
- Leverages F5's Ansible Imperative Collection for enhanced control of F5 devices.
- Reassigns application service roles to migrated services for continuity.

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

1. **main.yaml**:  
   - Orchestrates the migration process by dynamically identifying variables from Files/ips.csv.
   - Delegates tasks to `move_app.yaml`, `cs_names.yaml`, and `rbac.yaml`.

2. **move_app.yaml**:  
   - Uses the `bigiq_migrate_apps` role to migrate application services to the new BIG-IP instance.

3. **cs_names.yaml**:
   - Gathers the names of existing application services to pass them later to the RBAC playbook.

4. **rbac.yaml**
   - Assigns application service roles from the old services to the newly migrated services using the bigiq_apps_rbac role. 
   

#### Key Snippet from `main.yaml`:
```yaml
---
- name: Migrate Application Services to a new BIGIP
  hosts: iq
  connection: local
  gather_facts: false
  vars:
    timeout: 120
  tasks:
    - name: Load csv file to find the new target address
      community.general.read_csv:
        path: ../Files/ips.csv
      register: new_target

    - name: Process each Target address in the loop
      vars:
        current_target: "{{ ta.target_address }}"
        current_tenant: "{{ ta.tenantName }}"
        to_target: "{{ ta.new_target }}"
        new_tenant: "{{ ta.tenantName }}_new"
        move_to_app: "{{ ta.parentApplication }}"
      loop: "{{ new_target.list }}"
      loop_control:
        loop_var: ta
      ansible.builtin.include_tasks:
        move_app.yaml  
```
## CSV File Recommendation
This project relies on a CSV file (`Files/ips.csv`) to provide details about the source and target BIG-IP devices, application services, roles, and other variables for the migration process.

If you don't already have a CSV file prepared, we recommend using the following repository to gather and export the necessary CSV data from BIG-IQ:

- [**f5_big-iq_as3_rbac_export**](https://github.com/SalesAmerSP/f5_big-iq_as3_rbac_export)

This tool simplifies the process of exporting AS3 (Application Services) information, application roles, and relevant configurations into a compatible CSV format that can be directly used with the playbooks in this repository.

## Usage
Running the playbook
```bash
ansible-playbook playbooks/main.yaml
```
Running playbook example
```yaml
TASK [f5devcentral.bigiq_move_app_dashboard : Show all App Services to add into the Application in BIG-IQ dashboard] *****************************************************************************************
ok: [bigiq] => (item=[{'name': 'BIG_IQ_App'}, {'name': 'App_IQ_new_Luffy'}]) => {
    "msg": "Application Service App_IQ_new_Luffy belonging to BIG_IQ_App "
}
ok: [bigiq] => (item=[{'name': 'BIG_IQ_App'}, {'name': 'App_IQ_new_Zoro'}]) => {
    "msg": "Application Service App_IQ_new_Zoro belonging to BIG_IQ_App "
}

TASK [f5devcentral.bigiq_move_app_dashboard : Run task to move or merge and AS3 app in BIG-IQ dashboard] *****************************************************************************************************
included: /home/ecruz/Desktop/Ansible/Ansible/BIGIQ/roles/f5devcentral.bigiq_move_app_dashboard/tasks/move-merge.yaml for bigiq => (item=[{'name': 'BIG_IQ_App'}, {'name': 'App_IQ_new_Luffy'}])
included: /home/ecruz/Desktop/Ansible/Ansible/BIGIQ/roles/f5devcentral.bigiq_move_app_dashboard/tasks/move-merge.yaml for bigiq => (item=[{'name': 'BIG_IQ_App'}, {'name': 'App_IQ_new_Zoro'}])

TASK [f5devcentral.bigiq_move_app_dashboard : Show Application & Application Service] ************************************************************************************************************************
ok: [bigiq] => {
    "msg": "Application Service App_IQ_new_Luffy belonging to BIG_IQ_App"
} 
.......
TASK [Assign Application Service role to users with existing Application Role] *******************************************************************************************************************************
included: f5devcentral.bigiq_apps_rbac for bigiq => (item=App_IQ_Luffy)
included: f5devcentral.bigiq_apps_rbac for bigiq => (item=App_IQ_Zoro)
........
TASK [f5devcentral.bigiq_apps_rbac : Assign Application Service role to users with existing Application Role] ************************************************************************************************
skipping: [bigiq]

TASK [Resetting variables] ***********************************************************************************************************************************************************************************
ok: [bigiq]

TASK [Services array] ****************************************************************************************************************************************************************************************
ok: [bigiq] => {
    "msg": [
        []
    ]
}

PLAY RECAP ***************************************************************************************************************************************************************************************************
bigiq                      : ok=268  changed=18   unreachable=0    failed=0    skipped=92   rescued=0    ignored=0   
```
## Best Practices
- **Testing**: Use a staging environment to validate the playbooks before running them in production.
- **Error Handling**: Add error-handling tasks in your playbooks to gracefully handle failures.
- **Sensitive Data**: Use ansible-vault to encrypt sensitive information, such as inventory files or credentials.

## License
This project is licensed under the MIT License. See the LICENSE file for details.