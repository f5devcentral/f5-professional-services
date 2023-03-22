# awaf_policy_per_vs
A script that checks wheather a VS has a AWAF policy and if a policy is not prersent it will create one based on a AWAF parent policy.

# Usage

```
Within the script provide the following information:

device = "big-ip-301x-bigip1.fcruz" # Your BIG-IP FQDN or IP address
ltmDraft = "Drafts/"
asmParent = "Drafts" # Here you should relpace "Drafts" with the name of the Parent ASM policy

Then run the script and provide username and password of the target BIG-IP.

```

