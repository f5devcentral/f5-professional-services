output "name" {
    value = volterra_origin_pool.f5-origin.name
}

output "classified_origin_private" {
  value = local.classified_origin
}

output "private_origin" {
  value = local.private_origin
}