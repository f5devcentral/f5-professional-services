resource "volterra_certificate" "plain-text" {
  name            = "var.cert_name"
  namespace       = "var.namespace"
  certificate_url = "var.public_key"
  private_key {
    secret_encoding_type = "base64"
    clear_secret_info {
      url = "var.private_key"
    }
  }
}
