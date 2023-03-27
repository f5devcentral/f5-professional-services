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

|Time|Request ID|Event Type|Source IP address|X-Forwarded-For|Country|City|Browser|Domain|Method,Request Path|Response Code|
|----------|----------|----------|----------|1----------|----------|----------|----------|----------|----------|----------|----------|
|2023-03-27T18:45:29.881Z|be8c32c7-089f-43e8-9bcc-cf1829b05737|L7 Policy Violation|104.219.105.84|104.219.105.84|US|Seattle|curl|malvarado.f5-consult.f5pslab.com|DELETE|/|40|
|2023-03-27T14:21:03.955Z|6f419d86-3ba6-4884-860a-1016378e27ee|WAF|65.154.226.166|65.154.226.166|US|Santa Clara|HeadlessChrome|malvarado.f5-consult.f5pslab.com,GET|/js/bootstrap.min.js|200|
|2023-03-27T14:21:03.954Z|9d331638-130a-4221-be04-3a9fdcd050d8|WAF|65.154.226.166|65.154.226.166|US|Santa Clara|HeadlessChrome|malvarado.f5-consult.f5pslab.com,GET|/appliance.ssvg|200|
|2023-03-27T14:21:03.954Z|2e388f47-43cc-410b-9bd5-f08fecb119e6|WAF|65.154.226.166|65.154.226.166|US|Santa Clara|HeadlessChrome|malvarado.f5-consult.f5pslab.com|GET|/globe.ssvg|20|
