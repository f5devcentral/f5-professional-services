resource "null_resource" "f5_do_installer" {
  connection {
    type     = "ssh"
    host     = var.bigip_address
    user     = var.advanced_shell_user
    password = var.advanced_shell_user_password
    port     = "22"
  }
  provisioner "file" {
    #Uses the ssh connection to transfer the file to the BIG-IP system
    source      = "${var.f5_do_rpm_filename}.rpm"
    destination = "${var.do_install_dir}${var.f5_do_rpm_filename}.rpm"
  }

  provisioner "local-exec" {
    #curl command to install DO
    command = "curl -kvu admin:${var.admin_password} https://${var.bigip_address}/mgmt/shared/iapp/package-management-tasks -H \"Origin: https://${var.bigip_address}\" -H 'Content-Type: application/json;charset=UTF-8' --data '{\"operation\":\"INSTALL\",\"packageFilePath\":\"${var.do_install_dir}${var.f5_do_rpm_filename}.rpm\"}'"
  }

  provisioner "local-exec" {
    #Optional: This command verifies that the installation is successful. You should see: "class": "Result", "code": 200, "status": "OK"
    command = "sleep 3; curl -sku admin:${var.admin_password} https://${var.bigip_address}/mgmt/shared/declarative-onboarding/info"
  }


}
resource "bigip_do" "do-example" {
  do_json = file("do.json")
  depends_on = [ null_resource.f5_do_installer ]

}

resource "bigip_as3" "as3-example1" {
  as3_json = file("example1.json")
  depends_on = [bigip_do.do-example ]
}





