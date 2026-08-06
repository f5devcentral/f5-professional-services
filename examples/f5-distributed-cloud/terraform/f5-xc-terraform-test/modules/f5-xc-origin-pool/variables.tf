variable "namespace" {
  description = "XC Namespace"
  type = string
}

variable tenant {}

variable "origins" {
  description = "Origin Servers to create the Origin Pools"
  type = list(object({
    origin                = string  # Origin Server fqdn or IP address
    site                  = string
    virtual_site          = string
    network               = string # Network on the site: inside or outside
  }))
}

variable "port" {
  description = "Origin Server port."
  type        = string
}

variable "name" {
  description = "Origin Pool name"
  type = string
}

variable "healthcheck" {
  description = "Name of the health check object"
  type        = string
}

variable "use_tls" {
  description = "Determine if TLS will be used or not"
  type        = bool
  default     = true
}