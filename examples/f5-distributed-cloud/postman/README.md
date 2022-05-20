## Introduction
The provided Postman Collections are examples of how to accomplish the following tasks:

* Deploy New Applications
* Migrate Existing Applications (part of Deploy collection)
* Retrieve Data from the XC Tenant (WAF Logs, Configuration, CNAMES, etc)
* Delete Applications

Additionally, there are associated Postman Environments that need to be downloaded and used along with the Postman Collections

To Use, any of the content, download the **_collection.json+_environment.json** files, and import them into Postman


## **Postman Collections**
#### **F5-XC-Deploy-WAAP-(1 App)_collection.json.json**
Used to deploy individual applications.  

Collection contains subfolder with examples for the following tasks:
  * Deploy Single HTTP Application + WAAP for BYO Cert/Key + CNAME based DNS delegation
  * Deploy Single HTTP Application + WAAP for Auto Manage Cert+DNS (for zones delgetated to XC)

#### **F5-XC-Data-Retrieval_collection.json.json**
Used to retrieve logs and configuration information from a tenant/namespace/application

Collection contains subfolder with examples for the following tasks:
  * Retrieve HTTP App Config (1 App)
  * Retrieve HTTP App Configs (1 Namespace)
  * Retrieve WAF+HTTP Request Logs (1 App)
  * Retreive WAF+HTTP Requests Logs (Tenant)
  * Retreive HTTP LB CNAMES (Tenant) - also includes IP address Advertisements for each HTTP LB object
  
#### **F5-XC-Migrate_collection.json.json**
Used to migrate individual applications from one namespace to another.  Creates a new destination namespace if non-existent.

Collection contains subfolder with examples for the following tasks:
  * Migrate HTTP LB to new Namespace (1 App)

#### **F5-XC-Delete_collection.json.json**
Used to delete either individual HTTP LB+associated objects, or an entire namespace+associated shared objects

Collection contains subfolder with examples for the following tasks:
  * Delete App (1 App)
  * Delete Namespace + WAAP Shared Objects (1 App)  

## **Postman Environments**

##### Variables common to all collections:
  * **voltconsole-host** - shortname of the XC console host (example - if customer-a.console.ves.volterra.io is fqdn, then the value would be customer-a)
  * **tenant-id** - can be found under administration tab of the XC Console GUI
  * **api_credential** - needs to be generated from XC Console
  * **namespace_1** - namespace for data retrieval/deploy/delete
  * **app_name_1** - application object name for retreival/deploy/delete, used in context of namespace

#### **F5-XC-Deploy-WAAP-(1 App)_environment.json** 
Used to deploy individual applications.  Notes on some of the variables:
  * **pool_1** - may contain either FQDN values or IP addresses (multi-value, comma delimited)
  * **namespace_1-key** - Value may either be cleartext TLS key or Blindfold (recommended)
  * **apply_shared-appfw** - defaults to yes.  Creates+Applies a shared namespace WAF policy with default values for all settings
  * **apply_shared-svcpol** - defaults to yes.  Creates+Applies 2 shared namespace service policies in: one which geo-blocks OFAC countries, and another which allows ONLY GET/HEAD/POST HTTP menthods
  * **shared-appfw-name** - required if apply_shared-appfw variable is set to yes.  assign a name for the app firewall (WAF) object.

**Note:** If deploying an application using the auto-certificate+dns management the following variables are optional:
   * **namespace_1-cert**
   * **namespace_1-key**

#### **F5-XC-Migrate-(1 App)_environment.json**
More information to come!

#### **F5-XC-Data-Retrieval_environment.json**
More information to come!



