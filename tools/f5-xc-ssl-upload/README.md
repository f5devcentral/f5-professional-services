# Tools
## Terraform
### Clear Text
This tool allows uploading SSL private and public key pair to F5 XC tenant with Terraform module. It uses unencrypted base64 keys. Those keys stay unencrypted at rest in the XC tenant.
https://registry.terraform.io/providers/volterraedge/volterra/latest/docs/resources/volterra_certificate
### Blindfold
This tool allows uploading SSL private and public key pair to F5 XC tenant. It leverages vesctl for blindfolding the private keys . Private key is encrypted with vesctl before sending it to the tenant. The private key stays encrypted in the XC tenant. Please refer to: https://docs.cloud.f5.com/docs/how-to/advanced-security/blindfold-your-tls-certificates
## Bash
### blindfold.sh
This tool allows uploading SSL private and public key pair to F5 XC tenant by levreaging vesctl and bash. It allows of looping through directory of private and public keys and once the match of the pair is found, the blindfolded private key is sent to the XC tenant.
