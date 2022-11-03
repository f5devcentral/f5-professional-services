# F5 Cloud Failover Extension (CFE)

## Overview

This folder contains a [postman collection](postmanCollection.json) with APIs for the F5 Cloud Failover extension as well as examples for CFE for various public clouds (AWS, Azure, GCP).

For more information about F5 CFE, visit the [official documentation](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/#)  

## Quick API samples

```bash
# Obtain info about the CFE installed
curl -ku user:pass https://bigip/mgmt/shared/cloud-failover/info
```

```bash
# List associated cloud objects
curl -ku user:pass https://bigip/mgmt/shared/cloud-failover/inspect
```

```bash
# Obtain current declaration/configuration
curl -ku user:pass https://bigip/mgmt/shared/cloud-failover/declare
```

```bash
# Update declaration/configuration 
curl -ku user:pass -X POST https://bigip/mgmt/shared/cloud-failover/declare -d @cfe.json
```


```bash
# Trigger a dry-run failover
curl -ku user:pass -X POST https://bigip/mgmt/shared/cloud-failover/trigger -d '{"action":"dry-run"}' 
```

```bash
# Reset CFE configuration
curl -ku user:pass -X POST https://bigip/mgmt/shared/cloud-failover/reset -d '{"resetStateFile": true}' 
```
