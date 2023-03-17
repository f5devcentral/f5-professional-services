#Function:

This script will pull A record wideip hostnames from a BIGIP-DNS device (using iControl Rest), then perform a dig request on each name.  Hostname that was requested and the IP address response will be sent to stdout and written to a file with at file name corresponding to the target hostname or IP address provided when running the command with the current date ending in results.txt e.g. <hostname>.results<date>.txt


#Usage: 

wideipcheck.sh <GTM address> <Listener address> <Username>

#Example: 

ansible@raspi:~/scripts $ ./wideipcheck.sh dns.bigipdevices.local 10.0.0.253 admin
Enter Password:

There are 6 wide-ips in your configuration.

Lookups starting...


Lookups complete.


Results

algol.bigiplab.local  10.0.1.2
altair.bigiplab.local  10.0.1.2
demo.bigiplab.local  *** No response ***
mail.bigiplab.local  10.0.1.150
mail.algol.local  10.0.1.150
weather.bigiplab.local  10.0.1.4


