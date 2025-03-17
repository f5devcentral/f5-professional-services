# Description
This tool fetches the following data and exports to CSV file:
- namespace
- Origin Pool name
- Orign Pool advertise policy
- Origin Pool's attached load balancer
- FQDN
- Load Balancer's Advertise Policy
# Usage
1. Clone the repo and make the script executable. 
```
chmod +x f5-xc-advertise-policy-puller.sh
```
2. The script requires CSV file to be present before the execution but it will fill all required columns automatically.

``` 
touch global-advertise-policy.csv
```

3. Exucute the script and provide required information as command line arguements.

    To pull information from all namespaces:
    ```
    ./f5-xc-advertise-policy-puller.sh <myAPITOKEN1234> <my-xc-tenant> all
    ```

    To pull advertise policy from specific namespace:
    ```
    ./f5-xc-advertise-policy-puller.sh myAPITOKEN1234 my-xc-tenant my-xc-namespace
    ```

4. Expected output
```
Origin_Pool_name,Origin_Pool_site,namespace,LB_name,FQDN,LB_advertise_policy
my-pool,ce--us-east-1--prod-01,my-xc-namespace,my-lb,example.com,RE
```
