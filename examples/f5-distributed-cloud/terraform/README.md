# **Introduction**
The provided Terraform example to create a new WAAP protected HTTP application.  

This example creates the following objects:
* Health Check
* Origin Pool 
* HTTPS LB (autocert/DNS + WAF Policy)

# **Appendix**

### **Generate credentials (.p12)** 
Please create and download creadentials and store them in the **creds** folder

Create an **VES_P12_PASSWORD** environment variable with your credential password entered in F5 XC GUI/API during creation:
Example (in Linux)

```
export VES_P12_PASSWORD=password123!'
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

variable "domain" {
  default = "**yourdomain**"
} 


  
