data "vsphere_ovf_vm_template" "ovf-template" {
  name              = "ovf-template"
  disk_provisioning = "flat"
  resource_pool_id  = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id      = data.vsphere_datastore.datastore.id
  host_system_id    = data.vsphere_host.host1.id
  remote_ovf_url    = var.cluster_config.shared.ova_url
}

resource "vsphere_virtual_machine" "node1" {
  name                 = format("%s-%s-%s", var.vsphere_config.virtual_machine_prefix, var.cluster_config.shared.cluster_name, var.cluster_config.node1.hostname)
  datacenter_id        = data.vsphere_datacenter.datacenter.id
  datastore_id         = data.vsphere_datastore.datastore.id
  host_system_id       = data.vsphere_host.host1.id
  resource_pool_id     = data.vsphere_compute_cluster.cluster.resource_pool_id
  num_cpus             = data.vsphere_ovf_vm_template.ovf-template.num_cpus
  num_cores_per_socket = data.vsphere_ovf_vm_template.ovf-template.num_cores_per_socket
  memory               = 32768
  guest_id             = data.vsphere_ovf_vm_template.ovf-template.guest_id
  scsi_type            = data.vsphere_ovf_vm_template.ovf-template.scsi_type
  nested_hv_enabled    = data.vsphere_ovf_vm_template.ovf-template.nested_hv_enabled
  folder               = trimprefix(data.vsphere_folder.folder.path, "/${data.vsphere_datacenter.datacenter.name}/vm")

  network_interface {
    network_id = data.vsphere_network.outside.id
    ovf_mapping = "OUTSIDE"
  }

  network_interface {
    network_id = data.vsphere_network.inside.id
    ovf_mapping = "INSIDE"
  }

  disk {
    label       = "disk0"
    size        = 80
    unit_number = 0
  }

  wait_for_guest_net_timeout = 0
  wait_for_guest_ip_timeout  = 0

  ovf_deploy {
    allow_unverified_ssl_cert = false
    remote_ovf_url            = data.vsphere_ovf_vm_template.ovf-template.remote_ovf_url
    disk_provisioning         = data.vsphere_ovf_vm_template.ovf-template.disk_provisioning
  }

  vapp {
    properties = {
      "guestinfo.hostname" = var.cluster_config.node1.hostname
      "guestinfo.ves.token" = var.cluster_config.shared.token
      "guestinfo.ves.adminpassword": var.cluster_config.shared.admin_password
      "guestinfo.ves.clustername": var.cluster_config.shared.cluster_name
      "guestinfo.interface.0.name" = "eth0"
      "guestinfo.interface.0.dhcp" = "no"
      "guestinfo.interface.0.role" = "public"
      "guestinfo.interface.0.ip.0.address" = var.cluster_config.node1.addresses.outside
      "guestinfo.interface.0.route.0.gateway" = var.cluster_config.node2.route.gateway
      "guestinfo.interface.0.route.0.destination" = var.cluster_config.node2.route.destination
      "guestinfo.dns.server.0" = var.cluster_config.shared.dns_server1
      "guestinfo.dns.server.1" = var.cluster_config.shared.dns_server2
      "guestinfo.ves.regurl" = "ves.volterra.io"
      "guestinfo.ves.certifiedhardware"  = var.cluster_config.shared.certificate_hardware
      "guestinfo.ves.latitude" = var.cluster_config.shared.latitude
      "guestinfo.ves.longitude" = var.cluster_config.shared.longitude
    }
  }

}

resource "vsphere_virtual_machine" "node2" {
  name                 = format("%s-%s-%s", var.vsphere_config.virtual_machine_prefix, var.cluster_config.shared.cluster_name, var.cluster_config.node2.hostname)
  datacenter_id        = data.vsphere_datacenter.datacenter.id
  datastore_id         = data.vsphere_datastore.datastore.id
  host_system_id       = data.vsphere_host.host2.id
  resource_pool_id     = data.vsphere_compute_cluster.cluster.resource_pool_id
  num_cpus             = data.vsphere_ovf_vm_template.ovf-template.num_cpus
  num_cores_per_socket = data.vsphere_ovf_vm_template.ovf-template.num_cores_per_socket
  memory               = 32768
  guest_id             = data.vsphere_ovf_vm_template.ovf-template.guest_id
  scsi_type            = data.vsphere_ovf_vm_template.ovf-template.scsi_type
  nested_hv_enabled    = data.vsphere_ovf_vm_template.ovf-template.nested_hv_enabled
  folder               = trimprefix(data.vsphere_folder.folder.path, "/${data.vsphere_datacenter.datacenter.name}/vm")

  network_interface {
    network_id = data.vsphere_network.outside.id
    ovf_mapping = "OUTSIDE"
  }

  network_interface {
    network_id = data.vsphere_network.inside.id
    ovf_mapping = "INSIDE"
  }

  disk {
    label       = "disk0"
    size        = 80
    unit_number = 0
  }

  wait_for_guest_net_timeout = 0
  wait_for_guest_ip_timeout  = 0

  ovf_deploy {
    allow_unverified_ssl_cert = false
    remote_ovf_url            = data.vsphere_ovf_vm_template.ovf-template.remote_ovf_url
    disk_provisioning         = data.vsphere_ovf_vm_template.ovf-template.disk_provisioning
  }

  vapp {
    properties = {
      "guestinfo.hostname" = var.cluster_config.node2.hostname
      "guestinfo.ves.token" = var.cluster_config.shared.token
      "guestinfo.ves.adminpassword": var.cluster_config.shared.admin_password
      "guestinfo.ves.clustername": var.cluster_config.shared.cluster_name
      "guestinfo.interface.0.name" = "eth0"
      "guestinfo.interface.0.dhcp" = "no"
      "guestinfo.interface.0.role" = "public"
      "guestinfo.interface.0.ip.0.address" = var.cluster_config.node2.addresses.outside
      "guestinfo.interface.0.route.0.gateway" = var.cluster_config.node2.route.gateway
      "guestinfo.interface.0.route.0.destination" = var.cluster_config.node2.route.destination
      "guestinfo.dns.server.0" = var.cluster_config.shared.dns_server1
      "guestinfo.dns.server.1" = var.cluster_config.shared.dns_server2
      "guestinfo.ves.regurl" = "ves.volterra.io"
      "guestinfo.ves.certifiedhardware"  = var.cluster_config.shared.certificate_hardware
      "guestinfo.ves.latitude" = var.cluster_config.shared.latitude
      "guestinfo.ves.longitude" = var.cluster_config.shared.longitude
    }
  }

}

resource "vsphere_virtual_machine" "node3" {
  name                 = format("%s-%s-%s", var.vsphere_config.virtual_machine_prefix, var.cluster_config.shared.cluster_name, var.cluster_config.node3.hostname)
  datacenter_id        = data.vsphere_datacenter.datacenter.id
  datastore_id         = data.vsphere_datastore.datastore.id
  host_system_id       = data.vsphere_host.host3.id
  resource_pool_id     = data.vsphere_compute_cluster.cluster.resource_pool_id
  num_cpus             = data.vsphere_ovf_vm_template.ovf-template.num_cpus
  num_cores_per_socket = data.vsphere_ovf_vm_template.ovf-template.num_cores_per_socket
  memory               = 32768
  guest_id             = data.vsphere_ovf_vm_template.ovf-template.guest_id
  scsi_type            = data.vsphere_ovf_vm_template.ovf-template.scsi_type
  nested_hv_enabled    = data.vsphere_ovf_vm_template.ovf-template.nested_hv_enabled
  folder               = trimprefix(data.vsphere_folder.folder.path, "/${data.vsphere_datacenter.datacenter.name}/vm")

  network_interface {
    network_id = data.vsphere_network.outside.id
    ovf_mapping = "OUTSIDE"
  }

  network_interface {
    network_id = data.vsphere_network.inside.id
    ovf_mapping = "INSIDE"
  }

  disk {
    label       = "disk0"
    size        = 80
    unit_number = 0
  }

  wait_for_guest_net_timeout = 0
  wait_for_guest_ip_timeout  = 0

  ovf_deploy {
    allow_unverified_ssl_cert = false
    remote_ovf_url            = data.vsphere_ovf_vm_template.ovf-template.remote_ovf_url
    disk_provisioning         = data.vsphere_ovf_vm_template.ovf-template.disk_provisioning
  }

  vapp {
    properties = {
      "guestinfo.hostname" = var.cluster_config.node3.hostname
      "guestinfo.ves.token" = var.cluster_config.shared.token
      "guestinfo.ves.adminpassword": var.cluster_config.shared.admin_password
      "guestinfo.ves.clustername": var.cluster_config.shared.cluster_name
      "guestinfo.interface.0.name" = "eth0"
      "guestinfo.interface.0.dhcp" = "no"
      "guestinfo.interface.0.role" = "public"
      "guestinfo.interface.0.ip.0.address" = var.cluster_config.node3.addresses.outside
      "guestinfo.interface.0.route.0.gateway" = var.cluster_config.node2.route.gateway
      "guestinfo.interface.0.route.0.destination" = var.cluster_config.node2.route.destination
      "guestinfo.dns.server.0" = var.cluster_config.shared.dns_server1
      "guestinfo.dns.server.1" = var.cluster_config.shared.dns_server2
      "guestinfo.ves.regurl" = "ves.volterra.io"
      "guestinfo.ves.certifiedhardware"  = var.cluster_config.shared.certificate_hardware
      "guestinfo.ves.latitude" = var.cluster_config.shared.latitude
      "guestinfo.ves.longitude" = var.cluster_config.shared.longitude
    }
  }

}

resource "volterra_securemesh_site" "site" {
  
  name      = var.cluster_config.shared.cluster_name
  namespace = "system"

  blocked_services {
    blocked_sevice {
      web_user_interface = true
      network_type       = "network_type"
    }
  }

  no_bond_devices = true

  logs_streaming_disabled = true
  
  master_node_configuration {
    name      = var.cluster_config.node1.hostname
  }

  master_node_configuration {
    name      = var.cluster_config.node2.hostname
  }

  master_node_configuration {
    name      = var.cluster_config.node3.hostname
  }

  custom_network_config {

    interface_list {

      interfaces {

        ethernet_interface {

          device = "eth1"
          site_local_inside_network = true

          static_ip {
            cluster_static_ip {

              interface_ip_map {
                name = var.cluster_config.node1.hostname
                value {
                  ip_address = var.cluster_config.node1.addresses.inside
                }
              }

              interface_ip_map {
                name = var.cluster_config.node2.hostname
                value {
                  ip_address = var.cluster_config.node2.addresses.inside
                }
              }

              interface_ip_map {
                name = var.cluster_config.node3.hostname
                value {
                  ip_address = var.cluster_config.node3.addresses.inside
                }
              }


            }
          }
        }

      }

    }

    vip_vrrp_mode = "VIP_VRRP_ENABLE"

  }

  volterra_certified_hw  = var.cluster_config.shared.certificate_hardware

  depends_on = [
    vsphere_virtual_machine.node1,
    vsphere_virtual_machine.node2,
    vsphere_virtual_machine.node3
  ]

}

resource "volterra_registration_approval" "node1" {

  cluster_name  = var.cluster_config.shared.cluster_name
  hostname = var.cluster_config.node1.hostname
  cluster_size  = 3
  retry = 5
  wait_time = 300
  latitude = var.cluster_config.shared.latitude
  longitude = var.cluster_config.shared.longitude

  depends_on = [
    volterra_securemesh_site.site,
    vsphere_virtual_machine.node1
  ]
}

resource "volterra_registration_approval" "node2" {

  cluster_name  = var.cluster_config.shared.cluster_name
  hostname = var.cluster_config.node2.hostname
  cluster_size  = 3
  retry = 5
  wait_time = 300
  latitude = var.cluster_config.shared.latitude
  longitude = var.cluster_config.shared.longitude

  depends_on = [
    volterra_securemesh_site.site,
    vsphere_virtual_machine.node2
  ]
}

resource "volterra_registration_approval" "node3" {

  cluster_name  = var.cluster_config.shared.cluster_name
  hostname = var.cluster_config.node3.hostname
  cluster_size  = 3
  retry = 5
  wait_time = 300
  latitude = var.cluster_config.shared.latitude
  longitude = var.cluster_config.shared.longitude

  depends_on = [
    volterra_securemesh_site.site,
    vsphere_virtual_machine.node3
  ]
}

