terraform {
  required_providers {
    volterra = {
      source = "volterraedge/volterra"
      version = "0.11.49"
    }
  }
}

resource "volterra_app_firewall" "af" {
  name        = var.name
  namespace   = var.namespace
  blocking    = var.blocking
  default_detection_settings = true
  disable_ai_enhancements = true
  /*
  detection_settings {
    disable_staging = true
    violations_view {
      enabled = false
      enabled_by_default = false
      name = "VIOL_EVASION_APACHE_WHITESPACE"
      title = "Apache whitespace"
    }
    bot_protection_setting {
       good_bot_action       = "BLOCK"
       malicious_bot_action  = "REPORT"
       suspicious_bot_action = "IGNORE"
    }
  }
  */
   
  blocking_page {
    response_code = "Forbidden"
  }
  lifecycle {
    ignore_changes = [
      detection_settings
    ]
  }
}