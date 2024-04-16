#!/bin/bash
openssl x509 -text -in /config/httpd/conf/ssl.crt/server.crt
sleep 5s
cp /config/httpd/conf/ssl.crt/server.crt /config/httpd/conf/ssl.crt/server.crt.bak
cp /config/httpd/conf/ssl.key/server.key /config/httpd/conf/ssl.key/server.key.bak
tmsh save sys ucs /var/tmp/$HOSTNAME
