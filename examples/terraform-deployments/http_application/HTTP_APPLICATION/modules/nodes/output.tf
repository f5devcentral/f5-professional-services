//Following outputs will be exposed to use on the main.tf

output "ip_address" {
  value = bigip_ltm_node.node_test.address
  
}

output "node_name" {
  value= bigip_ltm_node.node_test.name
  
}