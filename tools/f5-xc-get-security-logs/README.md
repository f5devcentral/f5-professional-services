# xc_get_security_logs

The goal of this *Python* script is to help to export the Security Events logs from *F5 Distributed Cloud* via the XC API into a CSV file. T
The scripts save F5 XC security events to a CSV file named: security_events-<TENANT>-<NAMESPACE>_<date>-<hour>.csv
  
## Limitations

1. This version does not export Security Event logs for specific load balancer.

## Parameters

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| --domain | DNS forward zone to be converted | Yes | No |
| --nameserver | IP address of the NS server from which the zone transfer will be performed | Yes | No | 
| --tsig-key-name | TSIG key name | Yes | No | 
| --tsig-key-secret | TSIG key secret | Yes | No | 
| --tsig-key-algo | TSIG key algorithm | Yes | No | 

## Usage (examples)

### Example 1
```
python f5-xc-dns-create-zone-from-axfr.py\
               --domain "mydomain.com"\
               --nameserver "X.X.X.X"\
               --tsig-key-name "tsig-key."\
               --tsig-key-secret "UVXc0kf8FCPt4WVENnW6oMjpA/4tBHD25vXxYGd7uC6nD4xxyyxczucNEgalO3ZZk9LEqukeweZkZT3ajECIrg=="\
               --tsig-key-algo="hmac-sha512"
```

## Output - CSV file:
