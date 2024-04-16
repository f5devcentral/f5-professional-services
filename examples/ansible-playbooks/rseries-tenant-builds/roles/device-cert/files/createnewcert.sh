#!/bin/bash
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -sha256 -keyout /config/httpd/conf/ssl.key/server.key -out /config/httpd/conf/ssl.crt/server.crt -subj /CN=hostname.domain.net/L=Tampa/ST=Florida/O=F5/OU=IT/C=US/emailAddress=admin@domain.com
