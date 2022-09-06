# **Introduction**
The provided Terraform example to create a new WAAP protected HTTP application.  

This example creates the following objects:
* Health Check
* Origin Pool 
* HTTPS LB + WAF Policy (in blocking mode)

# **Appendix**
Creation 
  * **voltconsole-host** - shortname of the XC console host (example - if customer-a.console.ves.volterra.io is fqdn, then the value would be customer-a)
  * **tenant-id** - can be found under administration tab of the XC Console GUI
  * **api_credential** - needs to be generated from XC Console
  * **namespace_1** - namespace for data retrieval/deploy/delete
  * **app_name_1** - application object name for retreival/deploy/delete, used in context of namespace

### **Generate credentials (.p12)** 
  
