# Description
Sometimes it is required to pull all CE sites and virtual sites that are used by Origin Pools and Load Balancers to for example prepare for the CE backup or simply view which objects use which CE Site/Virtual Site. It becomes problematic to see that information from the console where there are many applications distributed in multiple namespaces. The script pulls that infromation and saves it in CSV file.

# Usage
1. Clone the repo and make the script executable. 
```
chmod +x f5-xc-advertise-policy-puller.sh
```
2. The script requires CSV file to be present before the execution but it will fill all required columns automatically.
``` 
toch vs.csv
```

3. Exucute the script and provide required information as command line arguements.

    To pull information from all namespaces:
    ```
    ./f5-xc-advertise-policy-puller.sh myAPITOKEN1234 my-xc-tenant all
    ```

    To pull advertise policy from specific namespace:
    ```
    ./f5-xc-advertise-policy-puller.sh myAPITOKEN1234 my-xc-tenant my-xc-namespace
    ```

4. Expected output
```
Origin_Pool_name,Origin_Pool_site,namespace,LB_name,FQDN
my-pool,ce--us-east-1--prod-01,my-xc-namespace,my-lb,example.com
```
