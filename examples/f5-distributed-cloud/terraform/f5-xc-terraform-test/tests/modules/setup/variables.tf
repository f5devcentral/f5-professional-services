# setup module variables

variable "tenant" {
  default = "**your-xc-tenant-id**"
}

variable "api_url" {
  default = "https://**your-xc-tenant-name**.console.ves.volterra.io/api"
}

variable "f5-xc_cert" {
  default = "./certs/xc.crt"
}
variable "f5-xc_key"  {
  default = "./certs/xc.key"
}

variable "namespace" {
  default = "**your-namespace**"  
}  