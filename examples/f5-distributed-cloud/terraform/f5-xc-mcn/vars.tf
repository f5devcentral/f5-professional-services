variable "name" {
  type    = string
  default = "t-mobile"
}

variable "namespace" {
  type    = string
  default = "p-kuligowski"
}

variable "aws_access_key" {
  sensitive = true
}
variable "aws_secret_key" {
  sensitive = true
}

## Vars for Azure CC
variable "client_id" {
  sensitive = true
}
variable "subscription_id" {
  sensitive = true
}

variable "tenant_id" {
  sensitive = true
}
variable "azure_secret_key" {
  sensitive = true
}

variable "gcp_secret" {
  sensitive = true
}
