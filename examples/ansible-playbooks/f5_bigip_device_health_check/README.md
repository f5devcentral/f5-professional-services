# f5_bigip_device_health.yml
## Overview

This Playbook will gather basic health information from the target BIG-IP.

**Information gathered:**
- CPU
- Memory
- Disk Space
- Interface status
- Version

Once the information is generated this playbook will save all the information in a file.

## Enviroment

1. Create a *Python3* virtual environment:

```
python3 -m venv myansible
```

2. Activate the virtual environment:

```
source myansible/bin/activate
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

1. Creating an Ansible.cfg file:

```
$ cat ansible.cfg
 
[defaults]
inventory = ./inventory
retry_files_enabled = False
host_key_checking = False
roles_path = roles
interpreter_python = python3
enable_task_debugger = True

```
2. Creating Ansible **Inventory**:

```
$ cat inventory/hosts

[bigips]
bigip1

[local]
localhost ansible_python_interpreter=/home/cisco/Desktop/Ansible/myansible/bin/python

$ cat inventory/hosts_vars/bigip1

ansible_host: A.A.A.A
ansible_user: admin
ansible_pass: admin

```

3. Create main playbook under **playbooks** Directory:

```
Here is where the playbook **f5_bigip_device_health.yml** will be placed

```
4. Create your **outputs** Directory:

```
Here is where the final file **health.txt** will be created 
 
```
Your enviroment should look as below:

```
├── README.md
├── ansible.cfg
├── inventory
│   ├── host_vars
│   │   └── bigip1
│   └── hosts
├── outputs
│   └── health.txt
└── playbooks
    └── f5_bigip_device_health.yml
 
```

## Running the playbook

```
ansible-playbook playbooks/f5_bigip_device_health.yml

PLAY [Test device Info] **********************************************************************************************************************************************************************

TASK [Checking Version] **********************************************************************************************************************************************************************
ok: [bigip1 -> localhost]

TASK [Checking Interfaces] *******************************************************************************************************************************************************************
ok: [bigip1 -> localhost]

TASK [Checking CPU health] *******************************************************************************************************************************************************************
ok: [bigip1 -> localhost]

TASK [Checking Memory health] ****************************************************************************************************************************************************************
ok: [bigip1 -> localhost]

TASK [Checking Disk Health] ******************************************************************************************************************************************************************
[WARNING]: Using "write" commands is not idempotent. You should use a module that is specifically made for that. If such a module does not exist, then please file a bug. The command in
question is "run util bash -c df -h..."
ok: [bigip1 -> localhost]

TASK [Deleting file if already exist.] *******************************************************************************************************************************************************
changed: [bigip1]

TASK [Creating a file to save the systme Health.] ********************************************************************************************************************************************
changed: [bigip1]

TASK [generating final file] *****************************************************************************************************************************************************************
changed: [bigip1]

PLAY RECAP ***********************************************************************************************************************************************************************************
bigip1                 : ok=8    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

```
## Final Output from **health.txt** File:

```

######## Device Health from A.A.A.A  ################
System running version: 14.1.5.3
Interfaces status: [
    "--------------------------------------------------------------",
    "Net::Interface",
    "Name  Status  Bits   Bits  Pkts   Pkts  Drops  Errs      Media",
    "                In    Out    In    Out                        ",
    "--------------------------------------------------------------",
    "1.1       up  2.5M   2.6M  7.7K   7.7K      0     0  10000T-FD",
    "1.2       up  2.5M  24.2M  7.7K  72.1K      0     0  10000T-FD",
    "mgmt      up  4.7M   8.3M  8.8K  13.0K      0     0   100TX-FD"
]
CPU Utilization is: [
    "System CPU Usage(%)  Current  Average  Max(since 03/22/23 08:41:48)",
    "-------------------------------------------------------------------",
    "Utilization                8        8                            15"
]
Memory Info: [
    "Sys::System Memory Information",
    "-----------------------------------------------------------------",
    "Memory Used(%)     Current  Average  Max(since 03/22/23 08:41:54)",
    "-----------------------------------------------------------------",
    "TMM Memory Used          4        4                             4",
    "Other Memory Used       55       55                            55",
    "Swap Used                0        0                             0"
]
Disk space Info: [
    "Filesystem                            1K-blocks    Used Available Use% Mounted on",
    "/dev/mapper/vg--db--vda-set.1.root       428150  138767    262759  35% /",
    "devtmpfs                                7970356       4   7970352   1% /dev",
    "tmpfs                                   7979460    2276   7977184   1% /dev/shm",
    "tmpfs                                   7979460    3124   7976336   1% /run",
    "tmpfs                                   7979460       0   7979460   0% /sys/fs/cgroup",
    "/dev/mapper/vg--db--vda-set.1._usr      5384128 4575120    512460  90% /usr",
    "/dev/mapper/vg--db--vda-set.1._config   2171984  269684   1772252  14% /config",
    "/dev/mapper/vg--db--vda-set.1._var      3030800  527764   2329368  19% /var",
    "none                                    7979460   22588   7956872   1% /var/tmstat",
    "prompt                                     4096      28      4068   1% /var/prompt",
    "/dev/mapper/vg--db--vda-dat.appdata    25717852  775648  23635788   4% /appdata",
    "/dev/mapper/vg--db--vda-dat.share      15350768  156396  14391556   2% /shared",
    "none                                    7979460   30140   7949320   1% /shared/rrd.1.2",
    "/dev/mapper/vg--db--vda-dat.log         2958224   82700   2705540   3% /var/log",
    "none                                    7979460       4   7979456   1% /run/pamcache",
    "none                                    7979460       0   7979460   0% /var/loipc",
    "/dev/loop0                               340398  340398         0 100% /var/apm/mount/apmclients-7230.2022.715.1725-6010.0.iso",
    "tmpfs                                   1595896       0   1595896   0% /run/user/91"
]
######## Device Health from A.A.A.A  ################
```
