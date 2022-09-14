# **Script to convert the EAP config to a human-readable file** #

The following script reads the EAP configuration and returns a human-readable file, organizing the configuration according to F5 XC objects.

**Use:**

Supply the EAP config file in JSON format as an argument.

*Example: ./GetInfoEAP.sh EAPconfig.json*

**Output:**
```
*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Load Balancer:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Main FQDN: "www.example.com"
Additionals FQDN: null
HTTP virtual server:true, redirect:true, port:80
HTTPS virtual server:true, port:443
Edpoints: , HTTPS:true, HTTP:true
_______________________________________________________________________________
Dataguard: true
_______________________________________________________________________________
Malicious IP:true and mode:"blocking"
Malicious IP Categories:
MOBILE_THREATS, block:true, log:true
CLOUD_SERVICES, block:true, log:true
ANONYMOUS_PROXIES, block:true, log:true
PHISHING_PROXIES, block:true, log:true
INFECTED_SOURCES, block:true, log:true
DENIAL_OF_SERVICE, block:true, log:true
SCANNERS, block:true, log:true
BOT_NETS, block:true, log:true
WEB_ATTACKS, block:true, log:true
WINDOWS_EXPLOITS, block:true, log:true
SPAM_SOURCES, block:true, log:true
TOR_PROXIES, block:true, log:true
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>App Firewall:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
High risk attack mitigation:true and mode:"blocking"
_______________________________________________________________________________
HTTP compliance enforcement:true
_______________________________________________________________________________
Threat_campaigns:true and mode:"blocking"
_______________________________________________________________________________
Sensitive parameters: true
Parameters List:
"cc_id"
"creditcard"
"passwd"
"password"
XML attributes List:

XML elements List:

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Service Policy:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
IP enforcement:true
IP addresses:
_______________________________________________________________________________
Geolocation_enforcement:true
Disallowed countries:
"Cuba"
"Iran (Islamic Republic of)"
"Korea (Democratic People's Republic of)"
"Libya"
"Sudan"
"Syrian Arab Republic"
_______________________________________________________________________________
Disallowed file types:true
File types List:
"back"
"bat"
"bck"
"bin"
"cfg"
"cmd"
"com"
"config"
"dat"
"dll"
"eml"
"exe"
"exe1"
"exe_renamed"
"hta"
"htr"
"htw"
"ida"
"idc"
"idq"
"ini"
"old"
"sav"
"save"
_______________________________________________________________________________
Method enforcement:true
Allowed methods List:
"GET"
"POST"
"HEAD"
_______________________________________________________________________________
Exceptions:
Cookies:

HTTP compliance:


Exceptions_parameters_objects
- Meta characters parameter name:

- Parameters names:
_______________________________________________________________________________
SignatureIDs:
```
