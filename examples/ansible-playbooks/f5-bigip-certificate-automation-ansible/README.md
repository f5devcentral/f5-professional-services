# f5-bigip-certificate-automation-ansible
## Overview

An *Ansible Playbook* to automate certificate management on BIG-IP.  

It will download the SSL/TLS certificate, key and (optionally) chain from the specified HTTPS URLs, install them on BIG-IP and them update the specified ClientSSL profile to use them. 

## How it works

The playbook will download the SSL/TLS certificate, key and (optionally) chain from the specified HTTPS URLs in a temporary location, compare the downloaded files with the ones hosted locally and which were installed the last time, if there is no difference, the installation is skipped, but if they changed, they will be installed on the BIG-IP, the specified *ClientSSL* profile will be updated to use them, (by default) the old certificate, key and (optionally) chain will be removed from the BIG-IP and the locally hosted files (cert/key/chain) will be updated. 

## Preparing the environment

1. Create a *Python3* virtual environment:

```
python3 -m venv virtualenv
```

2. Activate the virtual environment:

```
source virtualenv/bin/activate
```

3. Install *Ansible*:

```
pip install ansible
```

4. Install **F5 Ansible Imperative Collection**:

```
ansible-galaxy collection install f5networks.f5_modules
```

## Configuring the environment

1. Creating an Ansible *inventory* file:

```
cat << EOF > inventory/hosts
bigip1

[local]
localhost ansible_connection=local
  
EOF
```

2. Creating an Ansible *host_vars* file for the BIG-IP:

```
cat << EOF > inventory/host_vars/bigip1
ansible_host: A.A.A.A
ansible_user: admin 
ansible_pass: admin

EOF
```

3. Creating a **GLOBALCONFIG** file:

```
cat << EOF > vars/globalconfig/config.yaml
globalconfig:
  certificates_dir: "/opt/bigip/certificates"
  tmp_dir: "/opt/bigip/tmp"

EOF
```

The *certificates_dir* specify where in the system the certificates, keys and chains will be **permanently** stored. 
The *tmp_dir* specify where in the system the certificates, keys and chains will be **temporarily** stored (while the playbook is running). 

4. Creating the *tmp* and *certificates* directories specified in **GLOBALCONFIG** file:

```
mkdir -p /opt/bigip/certificates
mkdir -p /opt/bigip/tmp
```

5. Creating one or more **SSLCONFIG** files (one for each cert/key/chain you want to automate)

```
cat << EOF > vars/sslconfig/myapp1.yaml
sslconfig:
  cert_key_chain_name: "myapp1"
  cert_url: "https://webserver.f5trn.local/certificates/myapp1.crt"
  key_url: "https://webserver.f5trn.local/certificates/myapp1.key"
  chain_url: "https://webserver.f5trn.local/certificates/chain.crt"
  clientssl: "/Common/clientssl_myapp1"

EOF 
```
```
cat << EOF > vars/sslconfig/myapp2.yaml
sslconfig:
  cert_key_chain_name: "myapp2"
  cert_url: "https://webserver.f5trn.local/certificates/myapp2.crt"
  key_url: "https://webserver.f5trn.local/certificates/myapp2.key"
  clientssl: "/Common/clientssl_myapp2"

EOF 
```

6. Creating a *certificate* directory for each **SSLCONFIG** defined above:

```
mkdir /opt/bigip/certificates/myapp1
mkdir /opt/bigip/certificates/myapp2
```

## Running the playbook

1. Running the playbook:

```
ansible-playbook --extra-vars @vars/sslconfig/myapp1.yaml playbooks/playbook.yaml 

PLAY [F5 Certificate Automation] *****************************************************************************************************************************************************************************

TASK [Gathering Facts] ***************************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the tmp dir] *******************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Checking if the tmp dir exits] *************************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Get info of the certificates dir] **********************************************************************************************************************************************************************
ok: [bigip1]

TASK [Checking if the certificates dir exits] ****************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Checking if the SSLCONFIG variable was specified] ******************************************************************************************************************************************************
skipping: [bigip1]

TASK [Checking if the SSLCONFIG mandatory fields were specified] *********************************************************************************************************************************************
skipping: [bigip1]

TASK [Delete previous downloaded SSL certificate file] *******************************************************************************************************************************************************
ok: [bigip1]

TASK [Delete previous downloaded SSL key file] ***************************************************************************************************************************************************************
ok: [bigip1]

TASK [Delete previous downloaded SSL chain file] *************************************************************************************************************************************************************
ok: [bigip1]

TASK [Download SSL certificate] ******************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Download SSL key] **************************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Download SSL chain] ************************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Get info of the new certificate file] ******************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the new key file] **************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the new chain file] ************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the old certificate file] ******************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the old key file] **************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Get info of the old chain file] ************************************************************************************************************************************************************************
ok: [bigip1]

TASK [Import SSL certificate] ********************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Import SSL key] ****************************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Import SSL chain] **************************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Change ClientSSL profile (cert & key only)] ************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Change ClientSSL profile (cert, key & chain)] **********************************************************************************************************************************************************
changed: [bigip1]

TASK [Copy SSL certificate file] *****************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Copy SSL key file] *************************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Copy SSL chain file] ***********************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Delete old SSL chain file] *****************************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Get info of the currently assigned SSL cert/key/chain] *************************************************************************************************************************************************
ok: [bigip1]

TASK [Delete old SSL certificate] ****************************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Delete old SSL key] ************************************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Delete old SSL chain] **********************************************************************************************************************************************************************************
skipping: [bigip1]

TASK [Save the currently assigned SSL cert/key/chain] ********************************************************************************************************************************************************
changed: [bigip1]

TASK [Delete downloaded SSL certificate file] ****************************************************************************************************************************************************************
changed: [bigip1]

TASK [Delete downloaded SSL key file] ************************************************************************************************************************************************************************
changed: [bigip1]

TASK [Delete downloaded SSL chain file] **********************************************************************************************************************************************************************
changed: [bigip1]

PLAY RECAP ***************************************************************************************************************************************************************************************************
bigip1                     : ok=27   changed=14   unreachable=0    failed=0    skipped=9    rescued=0    ignored=0   
```


