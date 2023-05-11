
resource "bigip_do" "do-example" {
  do_json = file("do.json")
  depends_on = [ null_resource.f5_do_installer ]

}

resource "bigip_as3" "as3-example1" {
  as3_json = file("example.json")
  depends_on = [bigip_do.do-example ]
}





