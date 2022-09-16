# f5-backup-ansible.sh
## Overview

An Ansible Playbook to backup BIG-IP devices. 

It will create, download and remove an UCS archive from one or more BIG-IP devices. 

Main capabilities:

    - Does not fail immediately when the backup of one the BIG-IP device fails (will continue running the backup for all devices).
    - Record in a log file all backups that failed (including the reason of why the backup failed). 

## Preparing the environment

1. Create a *Python3* virtual environment:

```
python3 -m venv virtualenv
```

2. Activate the virtual environment:

```
source virtualenv/bin/activate
```

3. Install *Ansible*:

```
pip install ansible
```

4. Install **F5 Ansible Imperative Collection**:

```
ansible-galaxy collection install f5networks.f5_modules
```

## Configuring the environment

5. Configuring variables:

```
vim vars/config-vars.yaml
# The base directory in which the UCS archives will be stored. 
# Inside this directory, you must create a directory for each 
# BIG-IP device listed in your inventory. 
ucs_basedir: "/opt/f5-backup/backup"

# The log file in which you can find which backup tasks failed. 
logfile: "/opt/f5-backup/logs/f5-backup-ansible.log"

# A internal state file used to track if any backup task failed. 
statefile: "/opt/f5-backup/f5-backup-ansible.state"
```

6. Creating directories:

```
mkdir -p /opt/f5-backup/{backup,logs}
```

7. Configuring the *Ansible* inventory:

```
vim inventory/hosts
[bigips]
bigip1
bigip2
bigip3
bigip4

[local]
localhost ansible_connection=local
```

8. Create a *host_vars* file for each BIG-IP device:

```
vim inventory/host_vars/bigip1
ansible_host: A.A.A.A
ansible_user: admin 
ansible_pass: admin
```

```
vim inventory/host_vars/bigip2
ansible_host: B.B.B.B
ansible_user: admin 
ansible_pass: admin
```
```
vim inventory/host_vars/bigip3
ansible_host: C.C.C.C
ansible_user: admin 
ansible_pass: admin
```
```
vim inventory/host_vars/bigip4
ansible_host: D.D.D.D
ansible_user: admin 
ansible_pass: admin
```

9. Create the backup directory for each BIG-IP device:

```
mkdir -p /opt/f5-backup/backup/{bigip1,bigip2,bigip3,bigip4}
```

## Running the backup

10. Running the *F5 Backup Ansible* playbook:

```
ansible-playbook playbooks/f5-backup-ansible.yaml
```