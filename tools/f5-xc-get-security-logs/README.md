# xc_get_security_logs

This *Python* script helps to export the Security Events logs from *F5 Distributed Cloud* via the XC API into a CSV file.

The script generates a CSV file named as: security_events-\<TENANT\>-\<NAMESPACE\>_\<date\>-\<hour\>.csv

## Limitations

This version does not export Security Event logs for specific load balancer.

## Parameters

| Argument | Description | Required |
|----------|-------------|----------|
| --token | XC API Token | Yes | 
| --tenant | F5 Distributed Cloud Tenant name | Yes |
| --namespace | Namespace name | Yes |
| --hours | Time window in hours | Yes | 

## Usage:
```
python usage: xc_get_security_logs.py [-h] --token TOKEN --tenant TENANT --namespace NAMESPACE --hours HOURS

This *Python* script helps to export the Security Events logs from *F5 Distributed Cloud* via the XC API into a CSV file.

options:
  -h, --help            show this help message and exit
  --token TOKEN
  --tenant TENANT
  --namespace NAMESPACE
  --hours HOURS

The script generates a CSV file named as: xc-security_events-<TENANT>_<NAMESPACE>-<date>.csv
```
### Example:
```
python xc_get_security_logs.py\
               --token "A1B2C3D4E5F6G7H8I9K0"\
               --tenant "xc.tenant"\
               --namespace "my-namespace"\
               --hours 24
```

## Output - CSV file: 
xc-security_events-\<TENANT\>_\<NAMESPACE\>-MM-DD-YYYY.csv
