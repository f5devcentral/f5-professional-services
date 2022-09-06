# **Introduction**

Helper bash script to blindfold the TLS private key.  

Intended to be used along with other automation tools to assist with deployment of HTTPS LB on F5 Distributed Cloud

# **Instructions**

* Copy PEM output of your TLS private key
* Run Script and paste in TLS private key output
* Script will output a string containing the blindfolded key which can be used when deploying an HTTPS LB via API
