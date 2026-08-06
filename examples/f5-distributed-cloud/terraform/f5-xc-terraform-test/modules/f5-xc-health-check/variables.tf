variable "namespace" {
  description = "XC Namespace"
  type = string
}

variable "name" {
  description = "HTTP Health Check name"
  type        = string
}

variable "expected_status_codes" {
  description = "Status code for the health checks"
  type        = string
  default     = "200"
}