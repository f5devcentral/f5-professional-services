# **Introduction**
The provided Terraform example to create a new WAAP protected HTTP application.  

This example creates the following objects:
* HTTPS LB
* Origin Pool
* Health Check
* WAF Policy (in blocking mode)

  * **Delete App (1 App)**
  * **Delete Namespace + WAAP Shared Objects (1 App)**  

# **Notes**

### vairables.tf:
  * **voltconsole-host** - shortname of the XC console host (example - if customer-a.console.ves.volterra.io is fqdn, then the value would be customer-a)
  * **tenant-id** - can be found under administration tab of the XC Console GUI
  * **api_credential** - needs to be generated from XC Console
  * **namespace_1** - namespace for data retrieval/deploy/delete
  * **app_name_1** - application object name for retreival/deploy/delete, used in context of namespace

### **Generate credentials (.p12)** 
  * **pool_1** - origin pool member(s).  may contain either FQDN values or IP addresses (multi-value, comma delimited)
  * **namespace_1-key** - value may either be cleartext TLS key or Blindfold (recommended)
  * **apply_shared-appfw** - defaults to yes.  Creates+Applies a shared namespace WAF policy with default values for all settings
  * **apply_shared-svcpol** - defaults to yes.  Creates+Applies 2 shared namespace service policies in: one which geo-blocks OFAC countries, and another which allows ONLY GET/HEAD/POST HTTP menthods
  * **shared-appfw-name** - required if apply_shared-appfw variable is set to yes.  assign a name for the app firewall (WAF) object.
