terraform {
  required_providers {
    volterra = {
      source  = "volterraedge/volterra"
      version = "0.11.49"
    }
  }
}

resource "volterra_healthcheck" "origin-health-check" {
  name                = var.name
  namespace           = var.namespace
  healthy_threshold   = 1
  interval            = 15
  timeout             = 2
  unhealthy_threshold = 3

  http_health_check {
    use_origin_server_name = true
    path                   = "/"
    expected_status_codes  = [var.expected_status_codes]
  }
}