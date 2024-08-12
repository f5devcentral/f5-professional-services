# f5-awaf-attack-signature-enforcer

A tool written in *Go* to help manage and enforce attack signatures on a *BIG-IP Advanced WAF System*. 

It can be used to:

1. List all WAF policies on the system ( *-action list-waf-policies* ). 
2. List all attack signatures for a WAF policy and their respective status ( *-action list-attack-signatures* ). Optionally, a filter for the status can be specified. 
3. Print the *signatures enforcement readiness summary* for a specifc WAF policy or for all WAF policies on the system ( *-action print-enforcement-summary*).
4. Enforce all signatures which are *ready to be enforced* for a specific WAF policy ( *-action enforce-ready-signatures* ).

## Usage 

### Environment Variables

|  Variable Name  | Mandatory |          Description            |
|-----------------|-----------|---------------------------------|
| `BIGIP_ADDRESS` |    Yes    | BIG-IP IP address or hostname.   |
| `BIGIP_USERNAME`|    Yes    | BIG-IP admin username.           |
| `BIGIP_PASSWORD`|    Yes    | BIG-IP admin password.           |

### Command-line Options

|    Option   | Mandatory |        Default       |         Description            |
|-------------|-----------|----------------------|--------------------------------|
| `-action`   |    Yes    | *list-waf-policies*  | Specify the action which will be performed. Allowed values are: **list-waf-policies**, **list-attack-signatures**, **print-enforcement-summary**, and **enforce-ready-signatures**. |
| `-policy`   |    No     |                      | Specify the WAF policy in which the *action* will be applied. Mandatory for the actions *list-attack-signatures* and *enforce-ready-signatures*. Optional for the action *print-enforcement-summary* |
| `-sigstatus`|    No     |        *all*         |Specify a *status* filter when listing attack signatures. This option is optional and the allowed values are: **all**, **ready to be enforced**, **not enforced (has suggestions)**, **not enforced**, **enforced (has suggestions)**, and **enforced**. |

### Supported Actions

|            action          |         Description            |
|----------------------------|--------------------------------|
| `list-waf-policies`        | List all WAF policies on the system. |
| `list-attack-signatures`   | List all attack signatures for a specific WAF policy. The *-policy* is mandatory. |
| `print-enforcement-summary`| Print the *Signatures Enforcement Readiness Summary* for all WAF policies on the system or for a specific WAF policy (option *-policy*). |
| `enforce-ready-signatures` | Enforce all attack signature with a **ready to enforce** status for a specific WAF policy (option *-policy*).|

## Using

### Building

To build the tool, run:

```
go build -o f5-awaf-attack-signature-enforcer main.go awaf.go args.go
```

### Exporting Environment Variables

Before using this tool, it is needed to export a few required environment variables:

```
export BIGIP_ADDRESS="X.X.X.X"
export BIGIP_USERNAME="admin"
export BIGIP_PASSWORD="admin"
```

### Listing WAF policies

To list all WAF policies on the system, run:

```
./f5-awaf-attack-signature-enforcer -action list-waf-policies
```
```
policy                         id                        enforcementMode     
/Common/asmpolicy_app5         rBKYCfVhrFtCR-f-ARf2Vw    transparent         
/Common/asmpolicy_app4         zOVIyaxoJVb1Talpn1aedA    transparent         
/Common/asmpolicy_app3         XWPS7guLOaacZKlMlJWpGQ    blocking            
/Common/asmpolicy_app2         sgV4mAIDujF5f5LMoBJbUQ    blocking            
/Common/asmpolicy_app1         EpjFk_R-Eyi7fOxpy4i6BA    blocking                      
```

### Printing the Signatures Enforcement Readiness Summary

To print the *Signatures Enforcement Readiness Summary* for all WAF policies, run:

```
./f5-awaf-attack-signature-enforcer -action print-enforcement-summary
```
```
Policy                         | Total    | Not Enforced | Not Enforced (Have Suggestions)  | Ready To Be Enforced | Enforced | Enforced (Have Suggestions)   
/Common/asmpolicy_app2         | 2414     | 2412         | 1                                | 2411                 | 2        | 2                             
/Common/asmpolicy_app1         | 2414     | 2410         | 2                                | 2408                 | 4        | 1                             
/Common/asmpolicy_app5         | 3600     | 3600         | 0                                | 0                    | 0        | 0                             
/Common/asmpolicy_app4         | 3679     | 3679         | 0                                | 0                    | 0        | 0                             
/Common/asmpolicy_app3         | 3125     | 3125         | 3                                | 3122                 | 0        | 0                                                          
```

Or to print the *Signatures Enforcement Readiness Summary* for a specific WAF policy, run:

```
./f5-awaf-attack-signature-enforcer -action print-enforcement-summary -policy /Common/asmpolicy_app1
```
```
Total    | Not Enforced | Not Enforced (Have Suggestions)  | Ready To Be Enforced | Enforced | Enforced (Have Suggestions)   
2414     | 2410         | 2                                | 2408                 | 4        | 1                               
```

### Listing Attack Signatures

To list **all** attack signatures for a specific WAF policy, run: 

```
./f5-awaf-attack-signature-enforcer -action list-attack-signatures -policy /Common/asmpolicy_app1 
```
```
name                                               id                   learn           alarm           block           status                   
"sleep" injection attempt (URI)                    200104718            true            true            true            ready to be enforced     
"sleep" injection attempt (Header)                 200104717            true            true            true            ready to be enforced     
"sleep" injection attempt (Parameter)              200104716            true            true            true            ready to be enforced
...
XSS script target (Headers)                        200000094            true            true            true            ready to be enforced     
XSS script tag end (URI)                           200000093            true            true            true            ready to be enforced     
XSS script tag end (Headers)                       200000091            true            true            true            ready to be enforced     
<full output omitted>
```

To list all attack signatures with a specific status, use the command-line option *-sigstatus*. 

For example, to list all attack signatures with a status of **not enforced (has suggestions)**, run:

```
./f5-awaf-attack-signature-enforcer -action list-attack-signatures -policy /Common/asmpolicy_app1 -sigstatus "not enforced (has suggestions)"
```
```
name                                               id                   learn           alarm           block           status                   
<script>alert(1);</script> (Parameter)             200101609            true            true            true            not enforced (has suggestions)
XSS script tag end (Parameter) (2)                 200001475            true            true            true            not enforced (has suggestions)
```

To list all attack signatures with a status of **enforced**, run:

```
./f5-awaf-attack-signature-enforcer -action list-attack-signatures -policy /Common/asmpolicy_app1 -sigstatus "enforced"
```
```                  
name                                               id                   learn           alarm           block           status                   
" src http: (Header)                               200101559            true            true            true            enforced                 
" src http: (Parameter)                            200101558            true            true            true            enforced                 
"/.ftpconfig" access                               200010137            true            true            true            enforced              
```

Or to list all attack signatures with a status of **enforced (has suggestions)**, run:

```
./f5-awaf-attack-signature-enforcer -action list-attack-signatures -policy /Common/asmpolicy_app1 -sigstatus "enforced (has suggestions)"
```
```
name                                               id                   learn           alarm           block           status                   
XSS script tag (Parameter)                         200000098            true            true            true            enforced (has suggestions)
```

### Enforcing Attack Signatures Ready To be Enforced

To enforce all attack signatures which are **ready to be enforced** for a specific WAF policy, run:

```
./f5-awaf-attack-signature-enforcer -action enforce-ready-signatures -policy /Common/asmpolicy_app1
```
```
2408 signatures enforced.
Running an 'apply-policy' operation on the policy.
The 'apply-policy' task completed successfully.
```

To confirm that all **ready to be enforced** attack signatures were enforced, run:

```
./f5-awaf-attack-signature-enforcer -action print-enforcement-summary -policy /Common/asmpolicy_app1
```
```
Total    | Not Enforced | Not Enforced (Have Suggestions)  | Ready To Be Enforced | Enforced | Enforced (Have Suggestions)   
2414     | 2            | 2                                | 0                    | 2412     | 1                                               
```

