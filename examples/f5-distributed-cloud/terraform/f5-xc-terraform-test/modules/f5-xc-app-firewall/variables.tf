variable "namespace" {
  description = "XC Namespace"
  type        = string
}

variable "name" {
  description = "App Firewall Name"
  type        = string
}

variable "blocking" {
  description = "State of the App Firewall - blocking or monitoring"
  type        = bool
  default     = false
}