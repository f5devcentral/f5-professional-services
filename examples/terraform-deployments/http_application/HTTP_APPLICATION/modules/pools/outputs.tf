//Following output will be exposed to use on the main.tf

output "pool_name" {
    value = bigip_ltm_pool.pool.name
  
}
