# **Introduction**
The provided Terraform example to create a new WAAP protected HTTP application.  

This example creates the following objects:
* Health Check
* Origin Pool 
* WAF Policy with custom settings
* Service Policy to block OFAC countries, IP reputation assigned to the specified namespace
* HTTP LB (this example does not provide HTTPS) with Bot Defense, API discovery, WAF policy, L7 DoS, MAlicious User default

This example includes an optional sample tftest.hcl file to perform Unit and Integration testing using Terraform Test framework for different use cases:

* Validate that a required Service Policy is inherited from the namespace if the Load Balancer is advertised on the public network and the origin server is behind a Customer Edge
* Validate that a required Service Policy is applied directly to the Load Balancer if it is advertised on the public network and the origin server is behind a CE
* Check that an App Firewall policy is applied to the HTTP Load Balancer if it is advertised on the public network
* Verify that the Load Balancer name complies with the RFC 1035 Domain Names.
* Verify that the HTTP Load Balancer quota is not exceeded.

# **Appendix**

### **Generate XC credentials (.p12)** 
Please create and download XC API credentials certificate and store them in the **creds/** folder
https://docs.cloud.f5.com/docs/how-to/user-mgmt/credentials

Create an **VES_P12_PASSWORD** environment variable with your credential password entered in F5 XC GUI/API during creation:

Example (Linux):
```
export VES_P12_PASSWORD='password123!'
```

### **Extract the certificate and private key from the API Certificate required for the HTTP Data Source**
Extract the certificate:
openssl pkcs12 -in **your-xc-cred.p12** -clcerts -nokeys -out **your-xc-certificate**.crt

Extract the private key:
openssl pkcs12 -in **your-xc-cred.p12** -nocerts -nodes -out **your-xc-privatekey**.key

### Customize **terraform.tfvars.json**
Please modify the bold below strings in terraform.tfvars.json to match desired configuration output

{
    "tenant": "**your-xc-tenant-id**",
    "api_url": "https://**your-xc-tenant-name**.console.ves.volterra.io/api",
    "api_p12_file": "./certs/**your-xc-cred.p12**",
    "f5-xc_cert": "./certs/**your-xc-certificate**.crt",
    "f5-xc_key": "./certs/**your-xc-privatekey**.key",
    "base": "**demo-app**",
    "namespace": "**your-namespace**",
    "domains": ["**yourdomain1**","**yourdomain2**"],
    "origin_servers": [
      {
	    "origin": "**origin-ip-1**",
        "site": "",
        "virtual_site": "**virtual-site**",
        "network": "**inside**"
      },
      {
	    "origin": "**origin-ip-2**",
        "site": "",
        "virtual_site": "**virtual-site**",
        "network": "**outside**"
      }
    ],
    "environment": "**environment**",
    "waf_policy": **[true|false]**,
    "service_policy": [
      {
        "name": "**required-service-policy-1",
        "namespace": "**namespace**"
      },
      {
        "name": "**required-service-policy-2**",
        "namespace": "**namespace**"
      }
    ],
    "origin_pool_port": **origin-server-port**,
    "use_tls": **true|false**
}

### Customize **variables.tf** in setup module (./tests/modules/setup)
Please update the bolded values in variables.tf to match the expected configuration output for the Terraform test.

# setup module variables

variable "tenant" {
  default = "**your-xc-tenant-id**"
}

variable "api_url" {
  default = "https://**your-xc-tenant-name**.console.ves.volterra.io/api"
}

variable "f5-xc_cert" {
  default = "./certs/**your-xc-certificate**.crt"
}
variable "f5-xc_key"  {
  default = "./certs/**your-xc-privatekey**.key"
}

variable "namespace" {
  default = "**your-namespace**"  
}  