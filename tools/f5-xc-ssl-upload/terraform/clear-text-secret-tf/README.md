# Usage
### Copy your XC .p12 file to relevant location and fill variables.tf

## base64 your keys

```
cat cert.pem | base64
```

Paste base64 public and private key to variables.tf prefixed by "string:///"

## Apply terraform
```
terraform init
```

```
terraform plan
```

```
terraform apply
```
