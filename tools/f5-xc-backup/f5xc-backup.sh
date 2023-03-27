#!/bin/bash

##############################################									 
# F5 Distributed Cloud backup script: 
# Load Balancers, Origin Pools, Health Checks, 
# App Firewalls, Service Policies.             
##############################################

API_TOKEN=""
TENANT=""

DOMAIN=${TENANT}.console.ves.volterra.io
OUT_FLAG=1

### Prints section header
header() 
{
	printf	'\n%*.0s' ${#1} "" | tr " " "-"
	echo -e "\n${1}" 
	printf '%*.0s\n' ${#1}  "" | tr " " "-"
}

### Creates backup file and prints the header
file_backup()
{
	exec >"$TENANT"_${1}_backup_$(date +%m-%d-%Y).txt 
	echo -e "$TENANT Backup $(date +%m-%d-%Y)"
}

### Backup all application namespaces in a tenant
backup_all_ns() 
{
	file_backup "full"

	# Getting all namespace names
	NAMESPACES=$(curl --silent --location "https://${DOMAIN}/api/web/namespaces" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.items[]["name"]')

	# Getting objects for each namespace
	for NS in ${NAMESPACES}; do 
		# Get Load Balancers list
			header "Namespace: " ${NS}
			header "HTTP Load Balancers"
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS}/http_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
			header "TCP Load Balancers"
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS}/tcp_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
			header  "Origin pools"
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS}/origin_pools?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
			header "Health Checks"
			curl --silent --location --request GET "https://${DOMAIN}/api/config/namespaces/${NS}/healthchecks?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
			header "Application Firewall"
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS}/app_firewalls?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.namespace != ("shared"))'
			header "Service Policies"
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS}/service_policys?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.namespace != ("shared"))'
	done
}

### Backup specific application namespace
backup_namespace() 
{
	VALID_NS=$(curl --silent --location "https://${DOMAIN}/api/web/namespaces" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.items[]["name"] | select(. == "'"$NS_MNU"'")')
	if [ ! -z ${VALID_NS} ]; then
		file_backup "${NS_MNU}"
		header "Namespace: ${NS_MNU}"
		header "HTTP Load Balancers"
		curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
		header "TCP Load Balancers"
		curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/tcp_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
		header  "Origin pools"
		curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/origin_pools?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
		header "Health Checks"
		curl --silent --location --request GET "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/healthchecks?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
		header "Application Firewalls"
		curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/app_firewalls?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.namespace != ("shared"))'
		header "Service Policies"
		curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/service_policys?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.namespace != ("shared"))'
	else
		echo -e "\nThe namespace ${NS_MNU} doesn't exist!"
		OUT_FLAG=0
	fi
}

### Backup specific load balancer
backup_lb() 
{
    # Verify if namespace exists
	VALID_NS=$(curl --silent --location "https://${DOMAIN}/api/web/namespaces" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.items[]["name"] | select(. == "'"$NS_MNU"'")')
	if [ ! -z ${VALID_NS} ]; then
		# Verify if load balancer exists
		HTTP_LB=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.items[].name | select(. == "'"$2"'")')
		if [ ! -z ${HTTP_LB} ]; then
			
			file_backup ${HTTP_LB}
			header "Namespace: ${NS_MNU}"
			header "Load Balancer: ${LB_MNU}" 
			
			# Gets Load Balancer config
			curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}"

			# Gets pool list
			POOLS=$(curl --silent --location --request GET "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r .object.spec.gc_spec.default_route_pools[].pool.name)
			for pool in ${POOLS};do
				header "Origin pool: ${pool}"
				# Gets origin pools config
				curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/origin_pools/${pool}?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
				# Lists healthchecks
				HEALTHCHECKS=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/origin_pools/${pool}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r .object.spec.gc_spec.healthcheck[].name)
				# Gets healthchecks config
				for hc in ${HEALTHCHECKS};do
					header "Healthcheck: ${hc}"
					curl --silent --location --request GET "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/healthchecks/${hc}" --header "Authorization: APIToken ${API_TOKEN}"
				done
			done
		  
			# Gets Application Firewall
			read APPFW APPFWNS < <(echo $(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.object.spec.gc_spec.app_firewall | .name, .namespace'))

			header "Application Firewall: ${APPFW}"
			
			if [ ${APPFW} != null ]; then
				curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/app_firewalls?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.object.metadata.name =="'"$APPFW"'")'
			else
				echo -e "No Application Firewall"
			fi
		 
			header "Service Policies" 
			read NAMESPACE_SP SPECIFIC_SP NO_SP < <( echo $(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.object.spec.gc_spec | has("service_policies_from_namespace"), has("active_service_policies"),has("no_service_policies")'))
			
			# Gets Namespace service policies 
			if ${NAMESPACE_SP}; then
				NS_SRV_POL=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/active_service_policies" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.service_policies[].name')
				for SRV_POL in ${NS_SRV_POL};do
					header "Service Policy: ${SRV_POL}" 
					curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/service_policys?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.name =="'"$SRV_POL"'")'
				done   
			# Gets specific service policies
			elif ${SPECIFIC_SP}; then
				#echo -e "Specific Service Policies: ${SPECIFIC_SP}"
				SP_SERV_POLS=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/http_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.object.spec.gc_spec.active_service_policies.policies[].name')
				for SRV_POL in ${SP_SERV_POLS};do
					header "Service Policy: ${SRV_POL}" 
					curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/service_policys?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq '.items[] | select(.name =="'"$SRV_POL"'")'
				done
			else
				echo -e "No Service Policies"
			fi
		else
			# Verifies if TCP load balancer exists
			TCP_LB=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/tcp_loadbalancers?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r '.items[].name | select(. == "'"$2"'")')
			if [ ! -z ${TCP_LB} ]; then
				file_backup ${TCP_LB}
				header "Namespace: ${NS_MNU}"
				header "Load Balancer: ${LB_MNU}" 
				# Get TCP load balancer configuration
				curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/tcp_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
				# Gets Pool list
				POOLS=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/tcp_loadbalancers/${LB_MNU}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r .object.spec.gc_spec.origin_pools_weights[].pool.name)
				for pool in ${POOLS};do
					header "Origin pool: ${pool}"
					# Gets origin pools config
					curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/origin_pools/${pool}?report_fields" --header "Authorization: APIToken ${API_TOKEN}"
					# Lists healthchecks
					HEALTHCHECKS=$(curl --silent --location "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/origin_pools/${pool}?report_fields" --header "Authorization: APIToken ${API_TOKEN}" | jq -r .object.spec.gc_spec.healthcheck[].name)
					# Gets healthchecks config
					for hc in ${HEALTHCHECKS};do
						header "Healthcheck: ${hc}"
						curl --silent --location --request GET "https://${DOMAIN}/api/config/namespaces/${NS_MNU}/healthchecks/${hc}" --header "Authorization: APIToken ${API_TOKEN}"
					done
				done
			else
				echo -e "\n\nThe Load Balancer ${LB_MNU} doesn't exist!"
				OUT_FLAG=0
			fi
		fi	
	else
		echo -e "\n\nThe namespace ${NS_MNU} doesn't exist!"
		OUT_FLAG=0
	fi
}

### Main menu
header "F5 Distributed Cloud"
echo -e "\nWhat do you want to backup?\n"

options=("Tenant" "Namespace" "Load balancer" "Quit")
select OPT in "${options[@]}"
do
  case ${OPT} in
    "Tenant")
      echo -ne "Backing up F5XC $TENANT tenant namespaces configuration..." 
	  backup_all_ns
	  MNU="all"
	  break
      ;;
    "Namespace")
      echo "Enter namespace name: "
	  read NS_MNU
	  echo -ne "Backing up F5XC ${NS_MNU} namespace configuration..." 
	  backup_namespace "${NS_MNU}"
	  MNU="${NS_MNU}"
	  break
      ;;
    "Load balancer")
      echo "Enter namespace name: "
	  read NS_MNU
	  echo "Enter load balancer name: "
	  read LB_MNU
	  echo -ne "Backing up F5XC ${LB_MNU} load balancer configuration..." 
	  backup_lb "${NS_MNU}" "${LB_MNU}"
	  MNU=${LB_MNU}
      break
      ;;
    "Quit")
      exit 0
      ;;
   *) echo "Invalid option $REPLY";;
  esac
done

exec >&2
if [ ${OUT_FLAG} == 1 ]; then
	echo -e "\nBackup finished\n Output file: $(pwd)/"${TENANT}"_"${MNU}"_backup_$(date +%m-%d-%Y).txt"
fi
