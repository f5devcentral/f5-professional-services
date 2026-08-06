
output "app_lb_name" {
  value = volterra_http_loadbalancer.app-lb.name
}

output "app_lb_default_vip" {
  value = volterra_http_loadbalancer.app-lb.advertise_on_public_default_vip 
}

output "app_lb_ns_service_policies" {
  value = volterra_http_loadbalancer.app-lb.service_policies_from_namespace 
}

output "app_lb_app_firewall" {
  value = volterra_http_loadbalancer.app-lb.app_firewall[*].name
}

output "app_lb_active_service_policies" {
  value = volterra_http_loadbalancer.app-lb.active_service_policies[*].policies[*].name
}