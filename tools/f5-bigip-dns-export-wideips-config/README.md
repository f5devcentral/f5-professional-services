
# f5-bigip-dns-export-wideips-config

This *Python* script helps to export BIGIP's wideIP configuration to a CSV file.

The script generates a CSV file named as: WideIPInfo-\<hostname\>_\<date\>.csv

# How it Works

The script leverages the iControl REST API to retrieve the configuration of the wideIPs.

# Installation

pip3.X install -r requirements.txt

## Prerequisites

* Python 3.X+
* Libraries in requirements.txt
* The host machine needs to have access to the BIGIP.

## Usage:
```
Python3.X f5-export_wideip_config.py [-h] --bigip BIGIP --user USER --password PASSWORD

This *Python* script helps to export BIGIP's wideIPs configuration to a CSV file.

options:
  -h, --help           show this help message and exit
  --bigip BIGIP's IP address or hostname
  --user USER
  --password PASSWORD

The script generates a CSV file named as: WideIPInfo-<hostname>_<date>.csv
```
## Parameters

| Argument | Description | Required |
|----------|-------------|----------|
| --bigip | BIGIP's IP address or hostname | Yes | 
| --user | username | Yes |
| --password | password | Yes |


### Example:
```
python3.X ff5-export_wideip_config.py --bigip "<BIGIP's management IP>" --user "<username>" --passw "<password>"          
```

## Output - CSV file: 
WideIPInfo-\<BIGIP\>_MM-DD-YYYY.csv

| **WideIP**         | **Pools**                                                                               | **Last Resort Pool** | **Pool LB Mode**    | **Persistence** | **Persistence TTL** | **Persistence CIDR IPv4** | **Persistence CIDR IPv6** | **iRules**         |
|--------------------|-----------------------------------------------------------------------------------------|----------------------|---------------------|-----------------|---------------------|---------------------------|---------------------------|--------------------|
| example.wideip.lab | gtm_pool ;                                                             | none                 | round_robin         | disabled        | NA           | NA                 | NA                 | none               |
| gtm.wideip.lab     | gtm_pool_1; gtm_pool_2;                            | a /Common/gtm_pool   | global_availability | enabled         | 3600                | 24                        | 64                        | /Common/_iRule |
| j12412.wideip.lab  | gtm_pool; gtm_pool_1; gtm_pool_2; | a /Common/gtm_pool_1 | topology            | enabled         | 1564                | 32                        | 578                       | none               |
| test.wideip.lab    | gtm_pool; gtm_pool_1; gtm_pool_2; | none                 | ratio               | disabled        | NA           | NA                 | NA                 | /Common/_iRule |


