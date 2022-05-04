# f5-waf-quick-patch-CVE-2021-44228
F5 Networks Advanced WAF/ASM Quick Patch CVE 2021-44228.

# Overview

This tool connects to a BIG-IP device and creates a custom signature set called CVE-2021-4428 and apply it to all policies in blocking mode. It also enforces all signatures and apply the changes. This was tested on BIG-IP ASM v15.x but I believe it should work for v13.x/v14.x/v16.x.

WARNING: this procedure might increase CPU and memory on control plane usage while it is running.

# How it Works

The tool leverages BIG-IP iControl REST API to create the custom signature set as well to performs necessary changes to all policies.

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
