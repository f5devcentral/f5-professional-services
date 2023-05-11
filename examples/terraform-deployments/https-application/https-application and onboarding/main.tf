
resource "bigip_do" "do-example" {
  do_json = file("do.json")

}

resource "bigip_as3" "as3-example1" {
  as3_json = file("https_app_as3.json")
  depends_on = [bigip_do.do-example ]
}





