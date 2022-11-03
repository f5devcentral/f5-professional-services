# **Introduction**
The provided Terraform example to create multiple WAAP protected HTTP application based on a CSV input.  

This example creates the following objects:
* Health Check
* Origin Pool 
* HTTPS LB (autocert/DNS and/or custom cert + WAF Policy)

# **Appendix**

### **Generate XC credentials (.p12)** 
Please create and download XC credentials and store them in the **creds/** folder

Create an **VES_P12_PASSWORD** environment variable with your credential password entered in F5 XC GUI/API during creation:

Example (Linux):
```
export VES_P12_PASSWORD='password123!'
```

### Customize **variables.tf**
Please modify the bold below strings in variables.tf to match desired configuration output

variable "api_url" {
  default = "https://**yourtenant**.console.ves.volterra.io/api"
}

variable "api_p12_file" {
  default = "./creds/**your-cred.p12**"
}

variable "base" {
  default = "**demo-app**"
}

variable "namespace" {
  default = "**your-namespace**"
}  

### Customize input.csv
The following CSV fields need to be populated:

| Column                                         | Description |
| ----------------------------------------------- | ----------- |
| base_name | An application sufix name to be concatenated to the various objects to be created (e.g. app1) |
| fqdn | A single hostname for the load balancer (e.g. www.f5.com) |
| fe_port | The port for the load balancer (e.g. 443) |
| http_redirect | Indicates an automatic redirect from HTTP to HTTPS. Possible values: true, false |
| auto_cert | Indicates if a TLS certificate will be automatically generated. Possible values: true, false |
| origin_server | IP or fqdn of the origin server |
| origin_server_port | The port to connect to the origin server |
| origin_server_no_tls | Indicates if the connection to the origin server should NOT use TLS. Possible values: true, false | 
  
