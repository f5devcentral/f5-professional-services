# xc_get_security_logs

This *Python* script helps to export the Security Events logs from *F5 Distributed Cloud* via the XC API into a CSV file.

The script generates a CSV file named as: security_events-\<TENANT\>-\<NAMESPACE\>_\<date\>-\<hour\>.csv

## Limitations

1. This version does not export Security Event logs for specific load balancer.

## Parameters

| Argument | Description | Required |
|----------|-------------|----------|
| --domain | DNS forward zone to be converted | Yes | 
| --nameserver | IP address of the NS server from which the zone transfer will be performed | Yes |
| --tsig-key-name | TSIG key name | Yes |
| --tsig-key-secret | TSIG key secret | Yes | 
| --tsig-key-algo | TSIG key algorithm | Yes | 

## Usage (examples)

### Example:
```
python f5-xc-dns-create-zone-from-axfr.py\
               --domain "mydomain.com"\
               --nameserver "X.X.X.X"\
               --tsig-key-name "tsig-key."\
               --tsig-key-secret "UVXc0kf8FCPt4WVENnW6oMjpA/4tBHD25vXxYGd7uC6nD4xxyyxczucNEgalO3ZZk9LEqukeweZkZT3ajECIrg=="\
               --tsig-key-algo="hmac-sha512"
```

## Output - CSV file:
