# Overview

These *Python* scripts export the Security Events\Request Logs (i.e. API Access logs)\Audit Logs from *F5 Distributed Cloud* to a CSV file named: f5-xc-security_events\access_logs\audit_logs-<TENANT\>-\<NAMESPACE\>_\<date\>-\<hour\>.csv

# How it Works

The script leverages the F5 XC API to retrieve Security Events\Request Logs (i.e. API Access logs) for a specific HTTP load balancer protected by XC WAF (i.e. App Firewall). Alternatively, Audit Logs (including login events) can be pulled for the tenant across all namespaces.

# Installation

pip3.X install -r requirements.txt

## Prerequisites

* Python 3.X+
* Libraries in requirements.txt
* The host machine needs to have connection to the F5 Distribution Cloud Tenant.
* F5 XC API Token. Generate API Tokens: https://docs.cloud.f5.com/docs/how-to/user-mgmt/credentials#generate-api-tokens

## Usage:
```
python3.X f5-xc-export-security-event-logs.py [-h] --token TOKEN --tenant TENANT --namespace NAMESPACE --loadbalancer LOADBALANCER --hours HOURS

*Note: To run the audit log script, remove the "loadbalancer" flag. Everything else stays the same as if you were running the security event/request log scripts.*

options:
  -h, --help            show this help message and exit
  --token TOKEN
  --tenant TENANT
  --namespace NAMESPACE
  --loadbalancer LOADBALANCER *Note: See above. This flag doesn't apply for audit logs.*
  --hours HOURS, For Access Logs, max is 168 hour. For Security Events and Audit Logs, max is 720 hours.

```
## Parameters

| Argument | Description | Required |
|----------|-------------|----------|
| --token | F5 XC API Token | Yes |
| --tenant | F5 XC Tenant name | Yes |
| --namespace | Namespace name | Yes |
| --loadbalancer | Load balancer name | Yes |
| --hours | Time window in hours | Yes |

### Example:
```
python3.X f5-xc_get_security_logs.py\
               --token "A1B2C3D4E5F6G7H8I9K0"\
               --tenant "my-tenant"\
               --namespace "my-namespace"\
               --loadbalancer "my-loadbalancer"\
               --hours 24
```

## Output - CSV file:
f5-xc-security_events-\<TENANT\>_\<NAMESPACE\>-MM-DD-YYYY.csv
f5-xc-access_logs-\<TENANT\>_\<NAMESPACE\>-MM-DD-YYYY.csv
f5-xc-audit_logs-\<TENANT\>_\<NAMESPACE\>-MM-DD-YYYY.csv

| Time                | Request ID                           | Event Type          | Source IP address | X-Forwarded-For | Country | City        | Browser        | Domain     | Method | Request Path         | Response Code |
|:-------------------:|:------------------------------------:|:-------------------:|:-----------------:|:---------------:|:-------:|:-----------:|:--------------:|:----------:|:------:|:--------------------:|:-------------:|
| YYYY-MM-DDT00:00:01 | 00000000-0000-0000-0000-000000000000 | L7 Policy Violation | X.X.X.X           | X.X.X.X         | US      | Seattle     | curl           | example.com | DELETE | /                    | 403           |
| YYYY-MM-DDT00:00:02 | 00000000-0000-0000-0000-000000000001 | WAF                 | X.X.X.X           | X.X.X.X         | US      | Santa Clara | HeadlessChrome | example.com | GET    | /js/bootstrap.min.js | 200           |
| YYYY-MM-DDT00:00:03 | 00000000-0000-0000-0000-000000000002 | WAF                 | X.X.X.X           | X.X.X.X         | US      | Santa Clara | HeadlessChrome | example.com | GET    | /appliance.ssvg      | 200           |
