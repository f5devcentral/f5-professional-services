# x2f5 Universal Migration Tool

## Overview

The x2f5 tool is used to migrate configuration from other vendors to F5 in a standardised way. To add a new vendor, you only have to write the module. The tool uses python to parse the vendor configuration file and output the configuration in F5 syntax. Useful features such as updating objects and outputting config in JSON format make the tool a Swiss Army knife of config migration.

## Getting Started

### Installation

To install the tool, go to the homepage, download and unzip the package.

### Basic Usage

To use the tool, go to the directory and run the command `./x2f5.py <vendor> <inputfile>`

Note that the output configuration will be in the \<inputfile>_f5.cfg file.

Note the number of source objects parsed as well as errors / warnings.

#### Example

```bash
$ ./x2f5.py netscaler ns.conf
--------------------------------
-   F5 Configuration Convertor -
--------------------------------
Input filename:         ns.conf
Output filename:        ns.conf_f5.cfg
Partition:              /Common/
--- Device Details ---
Hostname:               netscaler
Software:               13.1 Build 50.23
Modules:

 - apm
Features:
--------
 - Web Logging
 - Load Balancing
 - Content Switching
 - Secure Sockets Layer
 - SSL VPN.
 - AAA
 - Rewrite.
 - Application Firewall.
 - Responder.
Modes:
-----
 - Fast Ramp
 - Edge configuration.
 - Use Subnet IP.
 - Path MTU Discovery.
 - Unified Logging Framework Mode for adding/removing ULF services

--- Source Configuration Object Count ---
 - Network -
Route Domains:          0
VLANS:                  6
Self IPs:               7
Routes:                 12
 - LTM -
Virtual Addresses:      107
Virtual Servers:        146
Pools:                  72
Nodes:                  78
Monitors:               14
Profiles:               28
Policies:               130
iRules:                 0
Errors
------
 - APM (SSL VPN) config is enabled but is not supported by this script
 - ASM/AWAF (AppFw) is enabled but is not supported by this script
 - Unknown monitor type localhost_ping for monitor PING, creating as TCP type
...```

```bash
$ ./x2f5.py -h
usage: x2f5.py [-h] [--output OUTPUT] [--update UPDATE] [--json] [--disable]
               [--debug] [--virtual VIRTUAL]
               {dummy,netscaler} inputfile [partition]

Config Converter to F5 Syntax

positional arguments:
  {dummy,netscaler}     Name of vendor
  inputfile             File containing vendor configuration
  partition             Optional partition name eg MyPartition

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output filename
  --update UPDATE       CSV-formatted modification file
  --json                Output config in JSON format
  --disable             Set all Virtual Addresses to disabled
  --debug               Turn on debugging
  --virtual VIRTUAL, -v VIRTUAL
                        Output a single virtual server
```

### Advanced Usage

## Support and Updates

There is no support implied in using this tool, it is used at your own risk.

However, if you would find bugs or would like a feature then please raise an issue via Github
