
# f5-bigip-ltm-export-vs-config

This *Python* script helps to export BIGIP's virtual server information to a CSV file.

The script generates a CSV file named as: VSInfo-\<hostname\>_\<date\>.csv

# How it Works

The script leverages the iControl REST API to retrieve the configuration of the virtual servers.

# Installation

pip3.X install -r requirements.txt

## Prerequisites

* Python 3.X+
* Libraries in requirements.txt
* The host machine needs to have access to the BIGIP.

## Usage:
```
Python3.X f5-export_vs_config.py [-h] --bigip BIGIP --user USER --password PASSWORD

This *Python* script helps to export BIGIP's virtual server information to a CSV file.

options:
  -h, --help           show this help message and exit
  --bigip BIGIP's IP address or hostname
  --user USER
  --password PASSWORD

The script generates a CSV file named as: VSInfo-<hostname>_<date>.csv
```
## Parameters

| Argument | Description | Required |
|----------|-------------|----------|
| --bigip | BIGIP's IP address or hostname | Yes | 
| --user | username | Yes |
| --password | password | Yes |


### Example:
```
python3.X f5-export_vs_config.py --bigip "<BIGIP's management IP>" --user "<username>" --passw "<password>"          
```

## Output - CSV file: 
VSInfo-\<BIGIP\>_MM-DD-YYYY.csv

| **Virtual Server** | **Source**       | **Destination**             | **Pool**                                      | **Profiles**                        | **SNAT**             | **Persistence** | **Fallback Persistence** | **iRule**                                       | **Traffic Polices**                         |
|--------------------|------------------|-----------------------------|-----------------------------------------------|-------------------------------------|----------------------|-----------------|--------------------------|-------------------------------------------------|---------------------------------------------|
| vs-l86sdh          | 103.245.56.12/32 | /Common/0.0.0.0:0           | /Common/pool-5Cu32kfytLq3yITvp15dLl5nCzjHUxQM | "clientssl, http, serverssl, tcp, " | /Common/my.SNAT.pool | source_addr     | /Common/dest_addr        | "/Common/_iRule, "                              | "my.traffic-policy, "                       |
| vs-proxy-8001      | 0.0.0.0/0        | /Common/10.245.245.200:8001 | /Common/pool-8001                             | "clientssl, http, serverssl, tcp, " | automap              | cookie          | none                     | "/Common/_iRule, "                              | none                                        |
| vs-proxy-8002      | 0.0.0.0/0        | /Common/10.245.245.200:8002 | /Common/pool-8002                             | "tcp, "                             | none                 | none            | none                     | none                                            | "my.second.ltm.policy, my.traffic-policy, " |
| vs.forwarding      | 10.10.10.0/24    | /Common/192.168.1.0:0       | none                                          | "fastL4, "                          | automap              | none            | none                     | none                                            | none                                        |
| vs.l4              | 0.0.0.0/0        | /Common/192.168.1.100:443   | /Common/pool-8002                             | "fastL4, http, "                    | automap              | cookie          | /Common/source_addr      | "/Common/_sys_https_redirect, /Common/_iRule, " | none                                        |

