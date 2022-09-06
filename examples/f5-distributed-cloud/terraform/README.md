# **Introduction**
The provided Terraform example to create a new WAAP protected HTTP application.  

This example creates the following objects:
* Health Check
* Origin Pool 
* HTTPS LB + WAF Policy (in blocking mode)

# **Appendix**

## **variables.tf**
Please modify the variables.tf to match desired configuration

  variable "api_url" {
  default = "https://**yourtenant**.console.ves.volterra.io/api"
}

variable "api_p12_file" {
  default = "./creds/your-cred.p12"
}

variable "base" {
  default = "demo-app"
}

variable "namespace" {
  default = "your-namespace"
}  

variable "domain" {
  default = "yourdomain"
} 

### **Generate credentials (.p12)** 
  
