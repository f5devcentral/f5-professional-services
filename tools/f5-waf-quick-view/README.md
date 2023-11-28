# f5-waf-quick-view
F5 Networks Advanced WAF/ASM Quick View.

# Overview

This tool connects to a BIG-IP device and performs a quick report on F5 WAF policies. The output is saved into a CSV file for further analysis inside data folder.

# How it Works

The tool leverages BIG-IP iControl REST API to query existent WAF policies and report aspects of the policies such as enforcement mode, signatures in staging, parent policy state etc.

## Prerequisites

Python 3.7+

Libraries in requirements.txt

The host machine needs to have connection to the BIG-IP management interface.

# Installation
1. Clone the repository to your machine:
  git clone https://github.com/f5devcentral/f5-professional-services.git

2. Go to the folder /f5-professional-services/tools/f5-waf-quick-view/

3. Install the requirements:

  pip3 install -r requirements.txt

# How to Use

1. Inside the folder /f5-professional-services/tools/f5-waf-quick-view/ edit the file devices.txt and add all BIG-IPs that you want to collect AWAF policies information. 

```
usage: f5-waf-quick-view.py [-h] device

positional arguments:
  device      a file containing list of BIG-IP devices separated by line, e.g. devices.txt | Example: f5-war-quick-view.py devices.txt

optional arguments:
  -h, --help  show this help message and exit

```
# Optional

1. Inside the folder /f5-professional-services/tools/f5-waf-quick-view/pbi there are a Microsoft Power BI files that show some graphics, please read the README.md file to get instructions how to use.


# Output Sample

![Alt text](csv.JPG?raw=true "f5-waf-quick-view")
