# Usage
## Download vesctl utility
Download vesctl and place it into your PATH location:
https://gitlab.com/volterra.io/vesctl/blob/main/README.md

## Configure vesctl config file
* download your .p12 and place into the relevant locations
* configure ./scripts/.vesconfig
* upload your certs in .PEM format to ./certs 

## Prepare Terraform
* configure variables.tf
* export VES_P12_PASSWORD=<your password>
* place your certs and relevant private keys in .PEM format to ./certs
* execute

```
terraform init -var="lb_cert=./certs/cert.pem" -var="lb_key=./certs/privkey.pem"
```
```
terraform plan -var="lb_cert=./certs/cert.pem" -var="lb_key=./certs/privkey.pem"
```
```
terraform apply -var="lb_cert=./certs/cert.pem" -var="lb_key=./certs/privkey.pem"
```
