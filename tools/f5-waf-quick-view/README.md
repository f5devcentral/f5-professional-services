# f5-waf-quick-view
F5 Networks Advanced WAF/ASM Quick View.

# Overview

This tool connects to a BIG-IP device and performs a quick report on F5 WAF policies. The output is saved into a CSV file for further analysis inside data folder.

# How it Works

The tool leverages BIG-IP iControl REST API to query existent WAF policies and report aspects of the policies such as enforcement mode, signatures in staging, parent policy state etc.

# Installation

pip3 install -r requirements.txt

## Prerequisites

Python 3.7+

Libraries in requirements.txt

The host machine needs to have connection to the BIG-IP management interface.

# How to Use

```
usage: f5-waf-quick-view.py [-h] device

positional arguments:
  device      IP adrresses of the target BIG-IP devices separated by line

optional arguments:
  -h, --help  show this help message and exit

```

# Output Sample

![Alt text](csv.JPG?raw=true "f5-waf-quick-view")
