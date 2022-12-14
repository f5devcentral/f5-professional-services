CREATED and TESTED SUCCESSFULLY BY STEVEN MEISENZAHL 11/19/2022

THIS PLAYBOOK USES THE RSERIES API TO BASE BUILD OUT AN RSERIES

THERE IS NO SUPPORT FOR THIS SOLUTION, USE AT YOUR OWN RISK
 
  INSTALL F5OS COLLECTION FOR ANSIBLE USING THE FOLLOWING LINK 
     "https://galaxy.ansible.com/f5networks/f5os"
 
  RUN THE FOLLOWING COMMAND FROM WITHIN "/root/.ansible/collections"
     ansible-galaxy collection install f5networks.f5os

  REFERENCE PAGES FOR THE BELOW TASKS CAN BE FOUND BY USING THE FOLLOWING LINK
    https://clouddocs.f5.com/training/community/rseries-training/html/introduction.html

  NOTE: For any API calls to the rSeries F5OS layer it is important to include the header Content-Type application/yang-data+json and use port 8888 

####################################################
Usage: ansible-playbook -vvv rseries-base-build.yaml
####################################################

The following is configured with this playbook
  Hostname
  Banner
  MOTD
  DNS
  NTP
  Remote Logging
  Portgroup Speeds
  Vlans
  Interfaces to Vlans
  LAGs
  Interfaces to LAGs
  LACP on LAGs
  SNMP Allow List
  SNMP Location
  SNMP Community
  SNMP Security View
  SNMP Traps
  SNMP Target
  
  Modify json files with your sites information and run the playbook
