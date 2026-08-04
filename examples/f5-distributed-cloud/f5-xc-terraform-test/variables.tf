variable "tenant" {
  description = "Tenant where the infrastructure will be deployed"
}

variable "api_url" {
  description = "Tenant API endpoint"
}

variable "api_p12_file" {
  description = "API Certificate for tenant authentication"
}

variable "f5-xc_cert" {
  description = "Certificate for API requests authentication"
}
variable "f5-xc_key" {
  description = "Private key for API requests authentication"
}

variable "base" {
  description = "Base object name"
}

variable "namespace" {
  description = "Namespace where the LB will be deployed"
}

variable "domains" {
  description = "List of domains to be associated with the Load Balancer"
  type        = list(string)
}

variable "origin_servers" {
  description = "Origin Servers to create the Origin Pools"
  type = list(object({
    origin                = string  # Origin Server fqdn or IP address
    site                  = string
    virtual_site          = string
    network               = string # Network on the site: inside or outside
  }))
}

variable "origin_pool_port" {
  description = "Port where origin service is hosted"
  type = number
}

variable "use_tls" {
  description = "Determine if Origin Pool TLS will be used or not"
  type        = bool
}

variable "service_policy" {
  description = "Service Policies to be associated with the Load Balancer"
  type = list(object({
    name      = string
    namespace = string
  }))
}

variable "waf_policy" {
  description = "Defines whether the App Firewall policy should be attached to the Load Balancer"
  type        = bool
}

variable "environment" {
  description = "The environemnt to deploy the resources to (dev, qa, prod)"
  type        = string
}