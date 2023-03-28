# f5-irule-letsencrypt
## Overview

An *iRule/iRule LX* which can be used to **deploy** and **expose** an HTTP-01 acme challenge in order to facilitate the generation of *Lets Encrypt* certificates.

## How it works

When applied to a Virtual Server, the iRule will expose the API endpoint **/api/letsencrypt** which can be consumed to deploy an HTTP-01 acme challenge. 

The acme challenge deployed is then exposed through the URI **/.well-known/acme-challenges/[ACME CHALLENGE]** which can be verified by the *Lets Encrypt* servers in order to generate the certificate. 

Although this iRule can be used independently, it was originally create to automate the generation of *Lets Encrypt* certificates through BIG-IQ.

## Configuring the iRule

1. Create an *LX Workspace* named **LetsEncrypt** ( *Local Traffic -> iRules -> LX Workspaces* ):

 ![LX Workskapce 1](/images/001.png)

 ![LX Workskapce 2](/images/002.png)

2. Add an *Extension* named **letsencrypt_ext** (*Add Extension* button):

 ![LX Extension 1](/images/003.png)

 ![LX Extension 2](/images/004.png)

3. Replace the content of the file *index.js* by the content of the file *letsencrypt.js* hosted on this repo (don't forget to click on *Save File*):

 ![LX Extension 3](/images/005.png)

4. Create an *LX Plugin* named **letsencrypt_pl** and selects the *LX Workspace* named **LetsEncrypt** (*Local Traffic -> iRules -> LX Plugins*):

 ![LX Plugin 1](/images/006.png)

 ![LX Plugin 2](/images/007.png)

5. Create a *Data Group* named **dg-letsencrypt-api-allowed-ips** and populates it with the IP addresses allowed to access the API endpoint **/api/letsencrypt**:

 ![Data Group](/images/008.png)

6. Create an *iRule* named **irule_letsencrypt** using the content of the file *irule_letsencrypt.tcl* hosted on this repo:

 ![iRule](/images/009.png)

7. Apply the *iRule* to the *Virtual Server*:

 ![Virtual Server](/images/010.png)

## Testing the iRule

1. Use the *curl* command to deploy an HTTP-01 acme challenge:

```
$curl -X POST "http://<VIP IP OR FQDN>/api/letsencrypt" -d @samples/challenges.json -H "Content-Type: application/json" -H "username: test" -H "password: test" 
{"status":"success", "message":"The HTTP-01 acme challenge will be automatically removed in 3600 seconds."}
```

2. Use the *curl* command to check the HTTP-01 acme challenge deployed:

```
$curl "http://<VIP IP OR FQDN>/.well-known/acme-challenge/uUrUgLtYtuX_-fWji1vHIicYfN_mVOT_r6tZAyZjm6I" 
uUrUgLtYtuX_-fWji1vHIicYfN_mVOT_r6tZAyZjm6I.xc1LuVlKDHQ77pXdV4CAF0PTZqyXAH4UZbHAyPz1nBU
```

## Configuring BIG-IQ

1. Create a *Third Party CA Management* named **LetsEncrypt_PROD** using *Lets Encrypt* as the *CA Provider* ( *Configuration -> Certificate Management -> Third Party CA Management*):

 ![Third Party CA Management 1](/images/011.png)

 ![Third Party CA Management 2](/images/012.png)

 2. Add a *Domain Configuration* entry to the *Third Party CA Management* created previously. 

 Configure the following values:

 - **Domain Name**: [VIP FQDN]
 - **API End Point**: http://[VIP FQDN]/api/letsencrypt
 - **User Name**: [the username defined in the iRule - static variable ```static::letsencrypt_username``` ]
 - **Password**: [the password defined in the iRule - static variable ```static::letsencrypt_password``` ]

Then click on *Save* 

![Third Party CA Management 3](/images/013.png)

Click on the *Domain Configuration* entry you added and then click on *Deploy & Test*:

![Third Party CA Management 4](/images/014.png)

3. Generate the Lets Encrypt certificate ( *Configuration -> Certificate Management -> Certificate & Keys* ): 

![Certificate & Key 1](/images/015.png)

![Certificate & Key 2](/images/016.png)

![Certificate & Key 3](/images/017.png)
