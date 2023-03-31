# F5 iRules

## Overview

This folder contains iRule samples for various functionalities.

## iRules 

| Example                                         | Description |
| ----------------------------------------------- | ----------- |
| [irule-cve-2022-22965](irule-cve-2022-22965.tcl)| This is a basic iRule to provide some mitigation against CVE-2022-22965 a.k.a. Spring4Shell. Tested on BIG-IP 15.x. |
| [f5-irule-letsencrypt](f5-irule-letsencrypt/)| An iRule/iRule LX which can be used to deploy and expose an HTTP-01 acme challenge in order to facilitate the generation of Lets Encrypt certificates. |