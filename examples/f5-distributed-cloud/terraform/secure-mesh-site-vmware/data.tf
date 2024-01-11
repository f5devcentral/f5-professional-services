data "vsphere_datacenter" "datacenter" {
  name = var.vsphere_config.datacenter
}

data "vsphere_compute_cluster" "cluster" {
  name = var.vsphere_config.compute_cluster
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_datastore" "datastore" {
  name = var.vsphere_config.datastore
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_host" "host1" {
  name = var.vsphere_config.hosts[0]
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_host" "host2" {
  name = var.vsphere_config.hosts[1]
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_host" "host3" {
  name = var.vsphere_config.hosts[2]
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_network" "outside" {
  name = var.vsphere_config.network_outside
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_network" "inside" {
  name = var.vsphere_config.network_inside
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_folder" "folder" {
  path = var.vsphere_config.folder
}