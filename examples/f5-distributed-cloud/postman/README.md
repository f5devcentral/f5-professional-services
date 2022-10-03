# Introduction
The provided Postman Collections are examples of how to accomplish the following tasks:

* Deploy New Applications
* Migrate Existing Applications
* Retrieve Data from the XC Tenant (WAF Logs, Configuration, CNAMES, etc)
* Deploy Brews Demo Application via vk8s cluster (can be via RE, CE, or RE+CE)
* Delete Applications

Additionally, there are associated Postman Environments that need to be downloaded and used along with the Postman Collections

To Use, any of the content, download the **_collection.json+_environment.json** files, and import them into Postman


# **Postman Collections**
### **F5-XC-Deploy_collection.json**
Used to deploy individual applications.  

Collection contains subfolder with examples for the following tasks:
  * **Deploy Single HTTP Application + WAAP Manual DNS/Cert (1 App)** - for BYO Cert/Key + CNAME based DNS delegation
  * **Deploy Single HTTP Application + WAAP Auto DNS/Cert (1 App)** - for Auto Manage Cert+DNS (DNS zones delgetated to XC)
  
**Note**: It is recommended to bindfold your TLS private key before deploying an HTTPS LB.  A helper script to accomplish this task can be found here: [xc-blindfold-script](https://github.com/f5devcentral/f5-professional-services/blob/main/tools/f5-xc-blindfold)


### **F5-XC-Data-Retrieval_collection.json**
Used to retrieve logs and configuration information from a tenant/namespace/application

Collection contains subfolder with examples for the following tasks:
  * **Retrieve HTTP App Config (1 App)**
  * **Retrieve HTTP App Configs (1 Namespace)**
  * **Retrieve WAF+HTTP Request Logs (1 App)**
  * **Retreive WAF+HTTP Requests Logs (Tenant)**
  * **Retreive HTTP LB CNAMES (Tenant)** - also includes IP address Advertisements for each HTTP LB object
  
### **F5-XC-Migrate_collection.json**
Used to migrate individual applications from one namespace to another.  Creates a new destination namespace if non-existent.

Collection contains subfolder with examples for the following tasks:
  * **Migrate HTTP LB to new Namespace (1 App)**

### **F5-XC-vk8s-MCN-Brews-App-Demo_collection.json**
Used to deploy Brews Demo Application using vk8s.  This is useful for showing off k8s and MCN functionality.  
Please use the accompanying environment included in this repo.
This collection is intended to be run in a single pass to deploy the demo application.  It may take 5-10 minutes after the collection is run for the site to be fully operational.  

**Note:**  It's assumed that your cloud sites (CE) have been deployed prior to using this collection.  

Collection contains subfolders with examples for the following deployment tasks:
  * **Cloud Sites Status**
  * **Base Config  (namespace, labels, waf policy)**
  * **vk8s&vsites**
  * **Workloads**
  * **Deployments (API+SPA)**
  * **LB + WAAP**

### **F5-XC-Delete_collection.json**
Used to delete either individual HTTP LB+associated objects, or an entire namespace+associated shared objects

Collection contains subfolder with examples for the following tasks:
  * **Delete App (1 App)**
  * **Delete Namespace + WAAP Shared Objects (1 App)**  

# **Postman Environments**

### Variables common to all environments:
  * **voltconsole-host** - shortname of the XC console host (example - if customer-a.console.ves.volterra.io is fqdn, then the value would be customer-a)
  * **tenant-id** - can be found under administration tab of the XC Console GUI
  * **api_credential** - needs to be generated from XC Console
  * **namespace_1** - namespace for data retrieval/deploy/delete
  * **app_name_1** - application object name for retreival/deploy/delete, used in context of namespace

### **F5-XC-Deploy_environment.json** 
Used to deploy individual applications.  Notes on some of the variables:
  * **pool_1** - origin pool member(s).  may contain either FQDN values or IP addresses (multi-value, comma delimited)
  * **namespace_1-key** - value may either be cleartext TLS key or Blindfold (recommended)
  * **apply_shared-appfw** - defaults to yes.  Creates+Applies a shared namespace WAF policy with default values for all settings
  * **apply_shared-svcpol** - defaults to yes.  Creates+Applies 2 shared namespace service policies in: one which geo-blocks OFAC countries, and another which allows ONLY GET/HEAD/POST HTTP menthods
  * **shared-appfw-name** - required if apply_shared-appfw variable is set to yes.  assign a name for the app firewall (WAF) object.

**Note:** If deploying an application using the auto-certificate+dns management the following variables are optional:
   * **namespace_1-cert**
   * **namespace_1-key**

### **F5-XC-Migrate_environment.json**
   * **namespace_1** - source namespace where application currently resides
   * **namespace_2** - target namespace where  application will be migrated

### **F5-XC-Data-Retrieval_environment.json**
   * **log_duration** - time frame for log retrieval.  interval can be hours or minutes (example:  5 min, 2 hours).  
   
     **Note:** Time will be time back from current time.  So if you put 1 hour, then you will get logs for the last 1 hour. 



