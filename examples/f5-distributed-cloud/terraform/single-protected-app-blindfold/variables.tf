variable "api_cert" {
        description = "API Certificate"
        type = string
        default = "./certs/<api credential certificate>.crt"
}
        
variable "api_key" {
        description = "API Private Key"
        type = string
        default = "./certs/<api credential key>.key"
}
        
variable "api_url" {
        description = "Tenant server URLs"
        type = string
        default = "https://<tenant_name>.console.ves.volterra.io/api"
}

variable "namespace" {
        description = "The namespace where the application will be deployed"
        default = "<namespace name>"
}

variable "app_domain" {
        description = "Application/Load balancer Domain name"
        default = "<domain name>"
}

variable "origin_server_dns" {
        description = "Public DNS Name of Origin Server"
        default = "<origin server dns name>"
}

variable "VES_PASSWORD" {
        description = "API Certificate .p12 password"
        type        = string
        sensitive   = true
}
variable "lb_key" {
        type = string
        description = "HTTP Load Balancer Private Key"
        validation {
                condition     = fileexists(var.lb_key) == true
                error_message = "Could not read private key from ${var.lb_key}"
        }
}
variable "lb_cert" {
        type = string
        description = "HTTP Load Balancer Certificate"
        validation {
                condition     = fileexists(var.lb_cert) == true
                error_message = "Could not read certificate from ${var.lb_cert}"
        }
}
