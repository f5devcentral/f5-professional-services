# compliance.tftest.hcl

run "global_setup" {
  # This block initializes a module to fetch information required for testing.

  module {
    source = "./tests/modules/setup"
  }
}

run "service_policy" {
  command =  plan
  variables {
    required_service_policies = "allow-vpn-ip-demo-sp"
  }

  # Check that a required Service Policy is inherited from the namespace if the Load Balancer is advertised on the public network and the origin server is behind a CE
  assert {
    condition = (
      module.http-lb.app_lb_default_vip == false ? true : 
      module.origin.private_origin == false ? true :
      (module.http-lb.app_lb_ns_service_policies == false ? true : contains(flatten(run.global_setup.xc_active_sp), var.required_service_policies))
    )
    error_message = "Service Policy \"${var.required_service_policies}\" must be associated with Load Balancer ${module.http-lb.app_lb_name} or inherited from the namespace."
  }

  # Check that a required Service Policy is applied directly to the Load Balancer if it is advertised on the public network and the origin server is behind a CE 
  assert {
    condition = (
      module.http-lb.app_lb_default_vip == false ? true :
      module.origin.private_origin == false ? true :
      (module.http-lb.app_lb_ns_service_policies == true ? true : contains(flatten(module.http-lb.app_lb_active_service_policies), var.required_service_policies))
    )
    error_message = "Service Policy \"${var.required_service_policies}\" must be explicitly associated with Load Balancer ${module.http-lb.app_lb_name} or inherited from the namespace."
  }
}

run "app_firewall" {
  command =  plan

  # Check that an App Firewall policy is applied to the HTTP Load Balancer if it is advertised on the public network
  assert {
    condition = module.http-lb.app_lb_default_vip == false ? true : length(module.http-lb.app_lb_app_firewall) > 0
    error_message = "An App Firewall must be associated with Load Balancer ${module.http-lb.app_lb_name} if advertised on Internet "
  }
}

run "http_load_balancer_name" {
  command = plan

  # Check that the Load Balancer name is correct
  assert {
    condition     = can(regex("^[a-z]([-a-z0-9]*[a-z0-9])?$", local.http-lb-name)) && length(local.http-lb-name) <= 63
    error_message = "The resource name must be a valid DNS-1035 label: 1-63 lower-case alphanumeric characters or '-', starting with a letter and ending with an alphanumeric character."
  } 
}

run "quota_usage" {
  command = plan

  # Check that the HTTP Load Balancer quota is not exceeded
  assert {
    condition = run.global_setup.xc_quota_usage["HTTP"] <= 200
    error_message = "HTTP Load Balancer quota exceeded"
  } 
}