# f5-bigip-declarative-waf-toolkit

*Python* script to manage *F5 Declarative WAF* policies. 

It can be used to:

1. Export a WAF policy in declarative format (JSON).
2. Export the *learning suggestions* for a WAF policy in declarative format (JSON).
3. Import a WAF policy from a *policy file* (JSON). Optionally, a *suggestions file* (JSON) containing learning suggestions can be specified in order to apply them to the policy. 
4. Export all WAF policies in declarative format (JSON).

# Working with F5 Declarative WAF

## Preparing environment variables

```
export BIGIP_ADDRESS="X.X.X.X"
export BIGIP_USERNAME="admin"
export BIGIP_PASSWORD="admin"
```

## Listing WAF policies (--action 'list-waf-policies')

To list all WAF policies:

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action list-waf-policies
```
```
1: /Common/asmpolicy_app4 (zOVIyaxoJVb1Talpn1aedA)
2: /Common/asmpolicy_app3 (XWPS7guLOaacZKlMlJWpGQ)
3: /Common/asmpolicy_app2 (sgV4mAIDujF5f5LMoBJbUQ)
4: /Common/asmpolicy_app1 (EpjFk_R-Eyi7fOxpy4i6BA)
```

## Exporting a WAF policy (--action 'export-waf-policy')

To export a WAF policy:

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-waf-policy --policy /Common/asmpolicy_app1 --output ./tmp/asmpolicy_app1.json
```
```
[INFO]: Exporting WAF policy '/Common/asmpolicy_app1' to the file './tmp/asmpolicy_app1.json'.
[INFO]: WAF policy successfully exported.
```

To export a WAF policy using **full** export mode (*--export-mode full*):

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-waf-policy --policy /Common/asmpolicy_app1 --output ./tmp/asmpolicy_app1.json --export-mode full
```
```
[INFO]: Exporting WAF policy '/Common/asmpolicy_app1' to the file './tmp/asmpolicy_app1.json'.
[INFO]: WAF policy successfully exported.
```

To export a WAF policy in **debug** mode (*--log-level debug*):

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-waf-policy --policy /Common/asmpolicy_app1 --output ./tmp/asmpolicy_app1.json --log-level debug
```
```
[INFO]: Exporting WAF policy '/Common/asmpolicy_app1' to the file './tmp/asmpolicy_app1.json'.
[DEBUG]: Retrieving WAF policies.
[DEBUG]: Starting new HTTPS connection (1): X.X.X.X:443
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/policies?$select=name,id,fullPath,link HTTP/11" 200 817
[DEBUG]: WAF policies successfully retrieved.
[DEBUG]: Running a 'export-policy' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-policy HTTP/11" 201 598
[DEBUG]: Waiting for the 'export-policy' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/2lFc6cXjd5ZL-z9zwUqQiw HTTP/11" 200 646
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/2lFc6cXjd5ZL-z9zwUqQiw HTTP/11" 200 646
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/2lFc6cXjd5ZL-z9zwUqQiw HTTP/11" 200 646
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/2lFc6cXjd5ZL-z9zwUqQiw HTTP/11" 200 646
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/2lFc6cXjd5ZL-z9zwUqQiw HTTP/11" 200 779
[DEBUG]: The 'export-policy' task completed successfully.
[DEBUG]: Downloading the exported WAF policy.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/file-transfer/downloads/Common-asmpolicy_app1.json HTTP/11" 200 8541
[DEBUG]: WAF Policy successfully downloaded.
[DEBUG]: Saving WAF policy to file.
[DEBUG]: WAF Policy sucessfully saved to file.
[INFO]: WAF policy successfully exported.
```

## Exporting Learning Suggestions (--action 'export-waf-suggestions')

To export the *learning suggestions* for a WAF policy:

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-waf-suggestions --policy /Common/asmpolicy_app1 --output ./tmp/asmpolicy_app1.suggestions.json
```
```
[INFO]: Exporting learning suggestions for the policy '/Common/asmpolicy_app1' to the file './tmp/asmpolicy_app1.suggestions.json'.
[INFO]: Learning suggestions successfully exported.
```

To export the *learning suggestions* for a WAF policy in **debug** mode (*--log-level debug*):

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-waf-suggestions --policy /Common/asmpolicy_app1 --output ./tmp/asmpolicy_app1.suggestions.json --log-level debug
```
```
[INFO]: Exporting learning suggestions for the policy '/Common/asmpolicy_app1' to the file './tmp/asmpolicy_app1.suggestions.json'.
[DEBUG]: Retrieving WAF policies.
[DEBUG]: Starting new HTTPS connection (1): X.X.X.X:443
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/policies?$select=name,id,fullPath,link HTTP/11" 200 1032
[DEBUG]: WAF policies successfully retrieved.
[DEBUG]: Running a 'export-suggestions' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-suggestions HTTP/11" 201 302
[DEBUG]: Waiting for the 'export-suggestions' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-suggestions/vV6o1QQJKUr-rLDvVc9hAg HTTP/11" 200 3391
[DEBUG]: The 'export-suggestions' task completed successfully.
[INFO]: Learning suggestions successfully exported.
```

## Importing a WAF policy:

To import a WAF policy **without** suggestions (only *--policy-file* option):

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action import-waf-policy --policy /Common/asmpolicy_app1 --policy-file ./tmp/asmpolicy_app1.json
```
```
[INFO]: Importing WAF policy '/Common/asmpolicy_app1' from file './tmp/asmpolicy_app1.json' (no suggestions).
[INFO]: WAF Policy successfully imported (no suggestions).
```

To import a WAF policy **with** suggestions (*--policy-file* and *--suggestions-file*):

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action import-waf-policy --policy /Common/asmpolicy_app1 --policy-file ./tmp/asmpolicy_app1.json --suggestions-file ./tmp/asmpolicy_app1.suggestions.json
```
```
[INFO]: Importing WAF policy '/Common/asmpolicy_app1' from file './tmp/asmpolicy_app1.json' with suggestions from './tmp/asmpolicy_app1.suggestions.json'.
[INFO]: WAF Policy successfully imported (suggestions applied).
```

## Exporting all WAF policies:

To export all WAF policies in a declarative format:

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-all-waf-policies --directory ./tmp
```
```
[INFO]: Exporting WAF policy '/Common/asmpolicy_app4' to the file './tmp/Common_asmpolicy_app4.json'.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app3' to the file './tmp/Common_asmpolicy_app3.json'.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app2' to the file './tmp/Common_asmpolicy_app2.json'.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app1' to the file './tmp/Common_asmpolicy_app1.json'.
[INFO]: WAF policy successfully exported.
```

To export all WAF policies in a declarative format using **full** export mode (*--export-mode full*) and with **debug** mode enabled:

```
python f5-bigip-declarative-waf-toolkit.py --device $BIGIP_ADDRESS --username $BIGIP_USERNAME --password $BIGIP_PASSWORD --action export-all-waf-policies --directory ./tmp --export-mode full --log-level debug
```
```
[DEBUG]: Retrieving WAF policies.
[DEBUG]: Starting new HTTPS connection (1): X.X.X.X:443
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/policies?$select=name,id,fullPath,link HTTP/11" 200 1032
[DEBUG]: WAF policies successfully retrieved.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app4' to the file './tmp/Common_asmpolicy_app4.json'.
[DEBUG]: Running a 'export-policy' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-policy HTTP/11" 201 599
[DEBUG]: Waiting for the 'export-policy' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/RAGAO3Mbem8nTme6ddCRRQ HTTP/11" 200 647
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/RAGAO3Mbem8nTme6ddCRRQ HTTP/11" 200 781
[DEBUG]: The 'export-policy' task completed successfully.
[DEBUG]: Downloading the exported WAF policy.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/file-transfer/downloads/Common-asmpolicy_app4.json HTTP/11" 200 79282
[DEBUG]: WAF Policy successfully downloaded.
[DEBUG]: Saving WAF policy to file.
[DEBUG]: WAF Policy sucessfully saved to file.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app3' to the file './tmp/Common_asmpolicy_app3.json'.
[DEBUG]: Running a 'export-policy' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-policy HTTP/11" 201 599
[DEBUG]: Waiting for the 'export-policy' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/1hNygdNygB0xs4vIPFEOpA HTTP/11" 200 647
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/1hNygdNygB0xs4vIPFEOpA HTTP/11" 200 781
[DEBUG]: The 'export-policy' task completed successfully.
[DEBUG]: Downloading the exported WAF policy.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/file-transfer/downloads/Common-asmpolicy_app3.json HTTP/11" 200 79282
[DEBUG]: WAF Policy successfully downloaded.
[DEBUG]: Saving WAF policy to file.
[DEBUG]: WAF Policy sucessfully saved to file.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app2' to the file './tmp/Common_asmpolicy_app2.json'.
[DEBUG]: Running a 'export-policy' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-policy HTTP/11" 201 598
[DEBUG]: Waiting for the 'export-policy' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/h0rfMIzpxbyKG7T0STPxgg HTTP/11" 200 646
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/h0rfMIzpxbyKG7T0STPxgg HTTP/11" 200 781
[DEBUG]: The 'export-policy' task completed successfully.
[DEBUG]: Downloading the exported WAF policy.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/file-transfer/downloads/Common-asmpolicy_app2.json HTTP/11" 200 79243
[DEBUG]: WAF Policy successfully downloaded.
[DEBUG]: Saving WAF policy to file.
[DEBUG]: WAF Policy sucessfully saved to file.
[INFO]: WAF policy successfully exported.
[INFO]: Exporting WAF policy '/Common/asmpolicy_app1' to the file './tmp/Common_asmpolicy_app1.json'.
[DEBUG]: Running a 'export-policy' task.
[DEBUG]: https://X.X.X.X:443 "POST /mgmt/tm/asm/tasks/export-policy HTTP/11" 201 599
[DEBUG]: Waiting for the 'export-policy' task to complete.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/6tlsIuw8sNWi2-Hf-0hjmQ HTTP/11" 200 647
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/tasks/export-policy/6tlsIuw8sNWi2-Hf-0hjmQ HTTP/11" 200 781
[DEBUG]: The 'export-policy' task completed successfully.
[DEBUG]: Downloading the exported WAF policy.
[DEBUG]: https://X.X.X.X:443 "GET /mgmt/tm/asm/file-transfer/downloads/Common-asmpolicy_app1.json HTTP/11" 200 79323
[DEBUG]: WAF Policy successfully downloaded.
[DEBUG]: Saving WAF policy to file.
[DEBUG]: WAF Policy sucessfully saved to file.
[INFO]: WAF policy successfully exported.
```