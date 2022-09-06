# **Introduction**

**For**: Preparation of TLS private keys on F5 Distributed Cloud Platform

**Description**: Bash script to blindfold the TLS private key prior to deployment to F5 XC config. 

# **Instructions**

* Ensure vesctl CLI tool is installed on the client machine.  Instructions can be found [here](https://gitlab.com/volterra.io/vesctl/-/tree/main)
* Download blindfold-xc-key.sh locally
* Create and download XC credentials and dowload them locally (should be in .p12 format)
* * Store the password as you will need it in the next step
* Separate .p12 file into key and certificate using openssl 
* Copy PEM output of your TLS private key
* Run Script and paste in TLS private key output
* Script will output a string containing the blindfolded key which can be used when deploying an HTTPS LB via API

