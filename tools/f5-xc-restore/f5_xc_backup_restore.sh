api_token=""
tenant=""
namespace=""

# Generate timestamp
timestamp=$(date +"%Y%m%d")

# Set log file path with timestamp
log_file="script_log_${timestamp}.txt"
> $log_file

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %T") $1" >> "$log_file"
}

# Check if the API token variable is set
if [ -z "$api_token" ]; then
    echo "Error: API token is not set."
    log "Error: API token is not set."
    exit 1
fi

# Check if the tenant variable is set
if [ -z "$tenant" ]; then
    echo "Error: Tenant is not set."
    log "Error: Tenant is not set."
    exit 1
fi

# Check if the namespace variable is set
if [ -z "$namespace" ]; then
    echo "Error: Namespace is not set."
    log "Error: Namespace is not set."
    exit 1
fi

# Script specific directories
load_balancers_dir="./load_balancers-${namespace}"
tcp_load_balancers_dir="./tcp_load_balancers-${namespace}"
origin_pools_dir="./origin_pools-${namespace}"
health_checks_dir="./health_checks-${namespace}"
service_policies_dir="./service_policies-${namespace}"
app_firewalls_dir="./app_firewalls-${namespace}"

# Check if the number of arguments provided is not equal to 1
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [backup | restore]"
    log "Usage: $0 [backup | restore]"
    exit 1
fi

# Check if the argument provided is either "backup" or "restore"
if [ "$1" != "backup" ] && [ "$1" != "restore" ]; then
    echo "Error: Invalid argument. Please provide 'backup' or 'restore'."
    log "Error: Invalid argument. Please provide 'backup' or 'restore'."
    exit 1
fi

# Create working directories if they don't exist
mkdir -p $load_balancers_dir $tcp_load_balancers_dir $origin_pools_dir $health_checks_dir $service_policies_dir $app_firewalls_dir
echo "Working directories created successfully."
log "Working directories created successfully."

#### MAIN ####
load_balancers_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/http_loadbalancers | jq -r .[][].name)"
tcp_load_balancers_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/tcp_loadbalancers | jq -r .[][].name)"
origin_pools_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools | jq -r .[][].name)"
health_checks_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/healthchecks | jq -r .[][].name)"
service_policies_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/service_policys| jq -r '.items[] | select(.namespace != "shared") | .name')"
app_firewalls_list="$(curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/app_firewalls| jq -r '.items[] | select(.namespace != "shared") | .name')"

echo "HTTP Applications in namespace: $namespace:"
log "HTTP Applications in namespace: $namespace:"
echo $load_balancers_list
log $load_balancers_list
echo
echo "TCP Applications in namespace: $namespace:"
log "TCP Applications in namespace: $namespace:"
echo $tcp_load_balancers_list
log $tcp_load_balancers_list
echo

# Main backup
if [ "$1" = "backup" ]; then
echo "=== Starting Backup ==="
log "=== Starting Backup ==="
sleep 1
  for load_balancer in $load_balancers_list; do
    echo
    echo "=== Backing up Load Balancer: $load_balancer ==="
    log "=== Backing up Load Balancer: $load_balancer ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/http_loadbalancers/$load_balancer > $load_balancers_dir/$load_balancer.json
    sleep 0.2
  done
  for tcp_load_balancer in $tcp_load_balancers_list; do
    echo
    echo "=== Backing up TCP Load Balancer: $tcp_load_balancer ==="
    log "=== Backing up TCP Load Balancer: $tcp_load_balancer ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/tcp_loadbalancers/$tcp_load_balancer > $tcp_load_balancers_dir/$tcp_load_balancer.json
    sleep 0.2
  done
  for origin_pool in $origin_pools_list; do
    echo
    echo "=== Backing up Origin Pools: $origin_pool ==="
    log "=== Backing up Origin Pools: $origin_pool ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools/$origin_pool > $origin_pools_dir/$origin_pool.json
    sleep 0.2
  done
  for health_check in $health_checks_list; do
    echo
    echo "=== Backing up Health Checks: $health_check ==="
    log "=== Backing up Health Checks: $health_check ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/healthchecks/$health_check > $health_checks_dir/$health_check.json
    sleep 0.2
  done
  for service_policy in $service_policies_list; do
    echo
    echo "=== Backing up Service Policies: $service_policy ==="
    log "=== Backing up Service Policies: $service_policy ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/service_policys/$service_policy > $service_policies_dir/$service_policy.json
    sleep 0.2
  done
  for app_firewall in $app_firewalls_list; do
    echo
    echo "=== Backing up App Firewalls: $app_firewall ==="
    log "=== Backing up App Firewalls: $app_firewall ==="
    curl -s -X GET -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/app_firewalls/$app_firewall > $app_firewalls_dir/$app_firewall.json
    sleep 0.2
  done
fi

# Main Restore
if [ "$1" = "restore" ]; then
# Check if folders contain minimum components to build Load Balancers
for dir in "$health_checks_dir" "$origin_pools_dir" "$load_balancers_dir" "$tcp_load_balancers_dir"; do
    if ! compgen -G "$dir/*.json" > /dev/null; then
        echo "!!! FOLDER $dir DOES NOT CONTAINT ANY .json FILES, ABORTING !!!"
        log "!!! FOLDER $dir DOES NOT CONTAINT ANY .json FILES, ABORTING !!!"
        exit 1
    fi
done
echo "=== Starting Restore ==="
sleep 1
# Restore Health Checks 
    for file in "$health_checks_dir"/*.json; do
    health_check_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring Health Checks: $health_check_name ==="
    log "=== Restoring Health Checks: $health_check_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/healthchecks -d "@$file")
    echo 
    if [ $response == 200 ]; then
        echo "Restored: $health_check_name"
        log "Restored: $health_check_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $health_check_name"
        log "Already exists: $health_check_name"
    else
        echo "Error occurred while restoring $health_check_name Please investigate."
        log "Error occurred while restoring $health_check_name Please investigate."
    fi
    sleep 0.5
  done
# Restore Origin Pools
    for file in "$origin_pools_dir"/*.json; do
    origin_pool_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring Origin Pools: $origin_pool_name ==="
    log "=== Restoring Origin Pools: $origin_pool_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/origin_pools -d "@$file")
    sleep 0.5
    if [ $response == 200 ]; then
        echo "Restored: $origin_pool_name"
        log "Restored: $origin_pool_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $origin_pool_name"
        log "Already exists: $origin_pool_name"
    else
        echo "Error occurred while restoring $origin_pool_name Please investigate."
        log "Error occurred while restoring $origin_pool_name Please investigate."
    fi
    sleep 0.5
  done
# Restore Service Policies but skip built-in ves-io policies
    for file in "$service_policies_dir"/*.json; do
    filename=$(basename -- "$file")
    if [[ $filename == *"ves-io"* ]]; then
        echo "Skipping file $file as its name contains 'ves-io'"
        log "Skipping file $file as its name contains 'ves-io'"
        continue
    fi   
    service_policy_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring Service policy: $service_policy_name ==="
    log "=== Restoring Service policy: $service_policy_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/service_policys -d "@$file")
    sleep 0.5
    if [ $response == 200 ]; then
        echo "Restored: $service_policy_name"
        log "Restored: $service_policy_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $service_policy_name"
        log "Already exists: $service_policy_name"
    else
        echo "Error occurred while restoring $service_policy_name. Please investigate."
        log "Error occurred while restoring $service_policy_name. Please investigate."
    fi
    sleep 0.5
    done
# Restore App Firewalls
    for file in "$app_firewalls_dir"/*.json; do
    app_firewall_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring App Firewalls: $app_firewall_name ==="
    log "=== Restoring App Firewalls: $app_firewall_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/app_firewalls -d "@$file")
    sleep 0.5
    if [ $response == 200 ]; then
        echo "Restored: $app_firewall_name"
        log "Restored: $app_firewall_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $app_firewall_name"
        log "Already exists: $app_firewall_name"
    else
        echo "Error occurred while restoring $app_firewall_name Please investigate."
        log "Error occurred while restoring $app_firewall_name Please investigate."
    fi
    sleep 0.5
  done
# Restore TCP Load Balancers
    for file in "$tcp_load_balancers_dir"/*.json; do
    tcp_load_balancer_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring TCP Load Balancers : $tcp_load_balancer_name ==="
    log "=== Restoring TCP Load Balancers : $tcp_load_balancer_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/tcp_loadbalancers -d "@$file")
    sleep 0.5
    if [ $response == 200 ]; then
        echo "Restored: $tcp_load_balancer_name"
        log "Restored: $tcp_load_balancer_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $tcp_load_balancer_name"
        log "Already exists: $tcp_load_balancer_name"
    else
        echo "Error occurred while restoring $tcp_load_balancer_name Please investigate."
        log "Error occurred while restoring $tcp_load_balancer_name Please investigate."
    fi
    sleep 0.5
  done
# Restore HTTP Load Balancers
    for file in "$load_balancers_dir"/*.json; do
    load_balancer_name=$(jq -r '.metadata.name' "$file") 
    echo
    echo "=== Restoring HTTP Load Balancers : $load_balancer_name ==="
    log "=== Restoring HTTP Load Balancers : $load_balancer_name ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: APIToken $api_token" https://$tenant.console.ves.volterra.io/api/config/namespaces/$namespace/http_loadbalancers -d "@$file")
    sleep 0.5
    if [ $response == 200 ]; then
        echo "Restored: $load_balancer_name"
        log "Restored: $load_balancer_name"
    elif [ $response == 409 ]; then
        echo "Already exists: $load_balancer_name"
        log "Already exists: $load_balancer_name"
    else
        echo "Error occurred while restoring $load_balancer_name Please investigate."
        log "Error occurred while restoring $load_balancer_name Please investigate."
    fi
    sleep 0.5
  done
fi

