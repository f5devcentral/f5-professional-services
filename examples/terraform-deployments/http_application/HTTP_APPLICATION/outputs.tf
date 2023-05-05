output "name_node" {
  value = module.nodes.node_name
}

output "ip_node" {
  value = module.nodes.ip_address

}

output "name_pool" {
  value = module.pools.pool_name
}

output "virtual_name" {
  value = bigip_ltm_virtual_server.http.name
}

output "virtual_adrress" {
  value = bigip_ltm_virtual_server.http.destination
}