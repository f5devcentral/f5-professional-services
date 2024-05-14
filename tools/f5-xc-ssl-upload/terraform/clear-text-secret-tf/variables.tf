variable "namespace" {
  description = "The namespace where the SSL will be deployed"
}

variable "p12" {
  description = "Path to XC p12 file"
}

variable "tenant_url" {
  description = "XC tenant URL, for example https://f5-consult.console.ves.volterra.io/api"
}
