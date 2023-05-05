terraform {
  required_providers {
    bigip = {
      source  = "F5Networks/bigip"
      version = ">= 1.16.0"
    }
  }
}
provider "bigip" {
  address  = "10.154.86.118"
  username = "admin"
  password = "karce123"

}

//Modules to create nodes, it will ask for a name and a description for the node, the remaining attributes will be inherited from the source module


module "nodes" {
  source      = "./modules/nodes"
  name        = var.node_name
  address     = var.node_address
  description = var.node_description

}

//Module to create pools, it will ask for a name and a description for the pool, the remaining attributes will be inherited from the source module

module "pools" {
  source      = "./modules/pools"
  name        = var.pool_name
  description = var.pool_description


}

// Resource to attach the nodes previously created and  to the pool previously created

resource "bigip_ltm_pool_attachment" "attach_node_to_pool" {
  pool       = module.pools.pool_name
  node       = "${module.nodes.node_name}:80"
  depends_on = [module.nodes] //Meta argument to create the resource only after the nodes are created
}

//Resource to create the virtual server

resource "bigip_ltm_virtual_server" "http" {
  name        = var.vs_name
  destination = var.vs_destination
  port        = var.vs_port
  pool        = module.pools.pool_name
  depends_on  = [bigip_ltm_pool_attachment.attach_node_to_pool] //Meta argument to create the resource only after the pool is created and have nodes attaches
}



