# f5-bigip-select-fact.yaml 

## Overview


    This playbook uses the bigip_device_info module to clollect a single fact from a bigip device (or devices).  


## How it works: 

   Playbook will output a list of possible options for devices facts to collect, then prompt you to select one. 
   Optionally you can uncomment the commented sections of the playbook and it will prompt you to save the file to the local host in the /var/tmp/ directory. 


## Running Playbook

    ansible-playbook <playbook dir>/bigip-select-fact.yml