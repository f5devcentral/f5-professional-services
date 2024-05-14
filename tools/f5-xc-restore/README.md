# F5 Distributed Cloud configuration backup and restore
## Intro
The script allows to backup and restore XC configurations of HTTP and TCP Load Balancers and their components. The script can be added to the crontab for daily backups:
```
crontab -e
55 23 * * * /backup/f5_xc_backup_restore.sh backup
```

## Usage
### Backup
* Set required variables inside of the script; api_token, tenant, namespace.
* Execute the script
  ```
  chmod +x f5_xc_backup_restore.sh
  ./f5_xc_backup_restore.sh backup
  ```
### Restore
* Set required variables inside of the script; api_token, tenant, namespace.
* The script checks if the required configurations JSONs are present (health checks, origin pools and HTTP loadbalancers)
* Execute the script
  ```
  chmod +x f5_xc_backup_restore.sh
  ./f5_xc_backup_restore.sh restore
  ```
