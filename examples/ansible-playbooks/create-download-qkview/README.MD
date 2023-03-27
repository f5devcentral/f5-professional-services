# f5-create-download-qkview.yaml 

## Overview


    This playbook will create a qkview of the targeted F5-BIGIP device(s) and save locally. 


## How it works: 

    The playbook will prompt you to enter your F5 case number, which will be used as part of the filename of the saved qkview, 
    along with the hostname of the device and the date the snapshot was taken.   The qkview file will be saved locally on the 
    ansible controller in the /var/tmp/ directory. 


## Running Playbook

    ansible-playbook playbooks/f5-create-download-qkview.yaml

## Example output

    An example of that the formating of the saved qkview file. 

    - dns1.57984.2023-03-17.qkview
    - <hostname><case number><date>.qkview
