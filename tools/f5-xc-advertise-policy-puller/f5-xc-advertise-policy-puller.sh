#!/bin/bash
api_token=$1
tenant=$2
namespace_provider=$3
csv_file="./vs.csv"

# Generate timestamp
timestamp=$(date +"%Y%m%d")

# Set log file path with timestamp
log_file="advertise_policy_log_${timestamp}.txt"
> "$log_file"

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %T") $1" | tee -a "$log_file"
}

# Check if the API token variable is set
if [ -z "$api_token" ]; then
    log "Error: API token is not set. Please provide token as the first argument."
    exit 1
fi

# Check if the tenant variable is set
if [ -z "$tenant" ]; then
    log "Error: Tenant is not set. Please provide tenant as the second argument."
    exit 1
fi

# Check if CSV file exists, or create it if not
if [ -e "$csv_file" ]; then
    log "The CSV file exists. Continuing..."
else
    log "Error: The CSV file does not exist. Please create vs.csv file."
    exit 1  
fi

# Prep CSV with headers
log "Preparing CSV"
echo "Origin_Pool_name,Origin_Pool_site,namespace,LB_name,FQDN" > "$csv_file"

#### MAIN ####
# Retrieve namespaces based on input
if [ "$namespace_provider" == "all" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/web/namespaces")
    
    if [ "$response" -ne 200 ]; then
        log "Error: Unable to connect to the namespaces API, HTTP status code $response"
        exit 1
    fi
    
    namespaces=$(curl -s -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/web/namespaces" | jq -r .[][].name)
    log "Collecting data from all namespaces"
elif [ -n "$namespace_provider" ]; then
    namespaces=$namespace_provider
    log "Starting data collection for specific namespace: $namespaces"
else
    log "No namespace provided! Use 'all' for all namespaces or specify a single namespace."
    exit 1
fi

log "Starting data collection."
# Loop through each namespace 
for namespace in $namespaces; do
    log "Starting data collection from namespace: $namespace"
    
    # Get origin pools for the namespace
    origin_pools=$(curl -s -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools" | jq -r .[][].name)
    
    # Loop through origin pools in the current namespace
    for origin in $origin_pools; do
        # Fetch Advertise Policy from Origin Pools
        origin_advertise_policy=$(curl -s -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools/$origin" | jq -r '.spec.origin_servers[0]? | (
        .private_ip? // .private_name // .k8s_service
        ) | .site_locator.virtual_site.name // .site_locator.site.name'
        ) 
        
        # Fetch Load Balancer details from Origin Pools
        origin_attached_lb=$(curl -s -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools/$origin?response_format=5" | jq -r '.referring_objects[0]?.name')
        
        # Fetch Domain from Load Balancer
        attached_lb_fqdn=$(curl -s -X GET -H "Authorization: APIToken $api_token" "https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/http_loadbalancers/$origin_attached_lb" | jq -r '.spec.domains[0]?')
        
        # Write to CSV
        line="$origin,$origin_advertise_policy,$namespace,$origin_attached_lb,$attached_lb_fqdn"
        echo "$line" >> "$csv_file"
        log "Collected: $line"
    done
done

log "Data collection complete."

