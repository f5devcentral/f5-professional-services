variable "namespace" {
  description = "The namespace where the SSL will be deployed"
}

variable "p12" {
  description = "Path to XC p12 file"
}

variable "tenant_url" {
  description = "XC tenant URL, for example https://f5-consult.console.ves.volterra.io/api"
}

variable "lb_key" {
  type        = string
  description = "HTTP Load Balancer Private Key"
  validation {
    condition     = fileexists(var.lb_key) == true
    error_message = "Could not read private key from ${var.lb_key}"
  }
}
variable "lb_cert" {
  type        = string
  description = "HTTP Load Balancer Certificate"
  validation {
    condition     = fileexists(var.lb_cert) == true
    error_message = "Could not read certificate from ${var.lb_cert}"
  }
}
