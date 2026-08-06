# setup module
# Fetch data from a REST API

data "http" "xc_quota_usage" {
  url = "${var.api_url}/web/namespaces/system/quota/usage"

  request_headers = {
    Accept        = "application/json"
  }
  client_cert_pem = file(var.f5-xc_cert)
  client_key_pem  = file(var.f5-xc_key)
}

data "http" "xc_active_sp" {
  url = "${var.api_url}/config/namespaces/${var.namespace}/active_service_policies"

  request_headers = {
    Accept        = "application/json"
  }
  client_cert_pem = file(var.f5-xc_cert)
  client_key_pem  = file(var.f5-xc_key)
}

# Use the response
locals {
  xc_quota_usage = jsondecode(data.http.xc_quota_usage.response_body)
  xc_active_sp   = jsondecode(data.http.xc_active_sp.response_body)
}

output "xc_quota_usage" {
  value = {
    "HTTP" = local.xc_quota_usage.objects.http_loadbalancer.usage.current
  }
}

output "xc_active_sp" {
  value = local.xc_active_sp.service_policies[*].name
}