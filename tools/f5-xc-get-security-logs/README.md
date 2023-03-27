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

| Time                | Request ID                           | Event Type          | Source IP address | X-Forwarded-For | Country | City        | Browser        | Domain     | Method | Request Path         | Response Code |
|:-------------------:|:------------------------------------:|:-------------------:|:-----------------:|:---------------:|:-------:|:-----------:|:--------------:|:----------:|:------:|:--------------------:|:-------------:|
| YYYY-MM-DDT00:00:01 | 00000000-0000-0000-0000-000000000000 | L7 Policy Violation | X.X.X.X           | X.X.X.X         | US      | Seattle     | curl           | exampe.com | DELETE | /                    | 403           |
| YYYY-MM-DDT00:00:02 | 00000000-0000-0000-0000-000000000001 | WAF                 | X.X.X.X           | X.X.X.X         | US      | Santa Clara | HeadlessChrome | exampe.com | GET    | /js/bootstrap.min.js | 200           |
| YYYY-MM-DDT00:00:03 | 00000000-0000-0000-0000-000000000002 | WAF                 | X.X.X.X           | X.X.X.X         | US      | Santa Clara | HeadlessChrome | exampe.com | GET    | /appliance.ssvg      | 200           |
