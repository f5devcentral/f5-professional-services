# f5-awaf-export-policies
A small script to export all AWAF policies from a BIG-IP device.

This script leverages BIG-IP iControl REST API to export ALL AWAF policies in the system and saves them locally. The policies can be exported in the following formats: xml, plc and json.

Note: JSON format only works with TMOS version 16.x. 

Tested with BIG-IP 16.1 but should work with older versions. 

# Usage

```
usage: f5-awaf-export-policies.py [-h] --device DEVICE --username USERNAME
                                  --password PASSWORD
                                  [--format {json,xml,plc}] [--output OUTPUT]

A small script to export all AWAF policies from a BIG-IP device.

optional arguments:
  -h, --help            show this help message and exit
  --device DEVICE, -d DEVICE
  --username USERNAME, -u USERNAME
  --password PASSWORD, -p PASSWORD
  --format {json,xml,plc}, -f {json,xml,plc}
  --output OUTPUT, -o OUTPUT

```

# Sample Output
```
$ python f5-awaf-export-policies.py -d 192.168.0.245 -u admin -p "XXXXXXX" -o ./output 
AWAF Policy /PartitionB/awaf_policy_app4 saved to file ./output/PartitionB-awaf_policy_app4.xml.
AWAF Policy /PartitionB/awaf_policy_app3 saved to file ./output/PartitionB-awaf_policy_app3.xml.
AWAF Policy /PartitionA/awaf_policy_app2 saved to file ./output/PartitionA-awaf_policy_app2.xml.
AWAF Policy /PartitionA/awaf_policy_app1 saved to file ./output/PartitionA-awaf_policy_app1.xml.
AWAF Policy /PartitionC/awaf_policy_app6 saved to file ./output/PartitionC-awaf_policy_app6.xml.
AWAF Policy /PartitionC/awaf_policy_app5 saved to file ./output/PartitionC-awaf_policy_app5.xml.

```
