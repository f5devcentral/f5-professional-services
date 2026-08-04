variable "tenant" {}

variable "namespace" {
  description = "XC Namespace"
  type = string
}

variable "origin_pool" {
  description = "Origin pool"
  type        = string
}

variable "name" {
  description = "LB name"
  type        = string
}

variable "app_firewall_name" {
  description = "App Firewall Name"
  type        = string
}

variable "domains" {
  description = "A list of domains"
  type        = list(string)
}

variable "use_tls" {
  description = "Determine if TLS will be used or not"
  type        = bool
  default     = true
}

variable "advertise" {
  description = "Determine if the LB will be advertised on the Internet or disabled"
  type       = bool
  default    = true
}

variable "enable_api_discovery" {
  description = "Controls whether to enable or not API discovery"
  type        = bool
  default     = false
}

variable "waf_policy" {
  description = "Defines whether the App Firewall policy should be attached to the Load Balancer"
  type        = bool
}

variable "service_policy" {
  description = "Service Policies to be associated with the Load Balancer"
  type        = list(object({
    name = string
    namespace = string
  }))
}
