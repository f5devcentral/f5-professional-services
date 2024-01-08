# Secure Mesh Site (VMware) deployment

This projects contains a *Terraform* script to deploy a *F5 Distributed Cloud Secure Mesh Site* in which the site nodes are running on a *VMWare* environment. 

The script performs the following steps:

- Deploy three *Customer Edges* nodes on a *VMWare* environment (e.g., **master-0**, **master-1**, **master-2**). The nodes are deployed in a multi-nic configuration connected to an **OUTSIDE** and an **INSIDE** networks.
- Create a *Secure Mesh Site* object on the *F5 Distributed Cloud* platform referecing the previously created nodes. The site is configured with a custom network configuration which will automatically configure the **INSIDE** network for the nodes.
- Approves all three nodes registration.

## Using

1. Configure the environment variables required by the *Terraform vSphere provider*:

```
$export VSPHERE_SERVER="<vsphere hostname or ip>"
$export VSPHERE_USER="<vsphere username>"
$export VSPHERE_PASSWORD="<vsphere password>"
```

2. On *F5 Distributed Cloud Console*, create a new *credential* and place it on the *creds* directory under the name *creds.p12*.

3. Configure the environment variable hosting the credential's password:

```
$export VES_P12_PASSWORD="<credential's password>"
```

4. Initialize the *Terraform* environment:

```
$terraform init
```

5. Create a *terraform.tfvars* file from the provided example and adjust it according to your environment:


```
cp terraform.tfvars.example terraform.tfvars
<using some editor, make the appropritate changes to the file>
```

6. Check the *Terraform* plan:

```
$terraform plan
```

7. Apply the *Terraform* plan:

```
$terraform apply
```
