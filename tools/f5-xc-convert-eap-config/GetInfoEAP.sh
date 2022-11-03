#!/bin/bash
# GetInfoEAP.sh
# Miguel Alvarado - m.alvarado@f5.com
# v1.0

# verify that we have correct number of arguments
if [ ! $# -eq 1 ];then
   echo -e "Please supply json file as argument; example:\r\n./GetInfoEAP.sh EAPconfig.json"
   exit 1
fi

file=$1
fqdn=$(cat $file | jq '.application.fqdn')
additional_fqdns=$(cat $file | jq '.application.additional_fqdns')

http=$(cat $file | jq '.application.http.enabled')
http_redirect=$(cat $file | jq '.application.http.https_redirect')
http_port=$(cat $file | jq '.application.http.port')

https=$(cat $file | jq '.application.https.enabled')
https_port=$(cat $file | jq '.application.https.port')

endpoints=$(cat $file | jq '.application.waf_regions | map(.[].endpoint.ips) | .[] | .[]')
endpoints_https_enabled=$(cat $file | jq '.application.waf_regions | map(.[].endpoint.https.enabled) | .[]')
endpoints_http_enabled=$(cat $file | jq '.application.waf_regions | map(.[].endpoint.http.enabled) | .[]')

dataguard_enabled=$(cat $file | jq '.policy.compliance_enforcement.data_guard.enabled')

malicious_ip_enforcement_enabled=$(cat $file | jq '.policy.malicious_ip_enforcement.enabled')
malicious_ip_enforcement_mode=$(cat $file | jq '.policy.malicious_ip_enforcement.enforcement_mode')
malicious_ip_enforcement_categories_length=$(cat $file | jq -r '.policy.malicious_ip_enforcement.ip_categories | length' )

malicious_ip_enforcement_enabled=$(cat $file | jq '.policy.malicious_ip_enforcement.enabled')
malicious_ip_enforcement_mode=$(cat $file | jq '.policy.malicious_ip_enforcement.enforcement_mode')

high_risk_attack_mitigation_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.enabled')
high_risk_attack_mitigation_enforcement_mode=$(cat $file | jq '.policy.high_risk_attack_mitigation.enforcement_mode')

http_compliance_enforcement_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.http_compliance_enforcement | .[]')

threat_campaigns_enabled=$(cat $file | jq '.policy.threat_campaigns.enabled')
threat_campaigns_enforcement_mode=$(cat $file | jq '.policy.threat_campaigns.enforcement_mode')

sensitive_parameters_enabled=$(cat $file | jq '.policy.compliance_enforcement.sensitive_parameters.enabled')
sensitive_parameters_list=$(cat $file | jq '.policy.compliance_enforcement.sensitive_parameters.parameters | .[]')
sensitive_xml_attributes_list=$(cat $file | jq '.policy.compliance_enforcement.sensitive_parameters.xml_attributes | .[]')
sensitive_xml_elements_list=$(cat $file | jq '.policy.compliance_enforcement.sensitive_parameters.xml_elements | .[]')

ip_enforcement_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.ip_enforcement.enabled')
ip_enforcement_length=$(cat $file | jq -r '.policy.high_risk_attack_mitigation.ip_enforcement.ips | length' )

geolocation_enforcement_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.geolocation_enforcement.enabled')
geolocation_disallowed_countries=$(cat $file | jq -r '.policy.high_risk_attack_mitigation.geolocation_enforcement.disallowed_country_codes | join(", ")')

disallowed_file_types_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.disallowed_file_types.enabled')
disallowed_file_list=$(cat $file | jq '.policy.high_risk_attack_mitigation.disallowed_file_types.file_types | .[]')

allowed_methods_enabled=$(cat $file | jq '.policy.high_risk_attack_mitigation.allowed_methods.enabled')
allowed_methods_list=$(cat $file | jq '.policy.high_risk_attack_mitigation.allowed_methods.methods | .[] | .[]')

exceptions_cookies_length=$(cat $file | jq -r '.policy.high_risk_attack_mitigation.exceptions.cookies | length')

exceptions_http_compliance=$(cat $file | jq '.policy.high_risk_attack_mitigation.exceptions.http_compliance | .[]')
exceptions_parameters_objects_meta_characters_param_name=$(cat $file | jq '.policy.high_risk_attack_mitigation.exceptions.parameters_objects.meta_characters_param_name | .[]')
exceptions_parameters_objects_parameter_names_length=$(cat $file | jq -r '.policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names | length')


echo -e ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Load Balancer:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
echo -e "Main FQDN: $fqdn\r\nAdditionals FQDN: $additional_fqdns"
echo -e "HTTP virtual server:$http, redirect:$http_redirect, port:$http_port"
echo -e "HTTPS virtual server:$https, port:$https_port"
echo -e "Edpoints: $endpoints, HTTPS:$endpoints_https_enabled, HTTP:$endpoints_http_enabled"
echo -e "_______________________________________________________________________________"
echo -e "Dataguard: $dataguard_enabled"
echo -e "_______________________________________________________________________________"
echo -e "Malicious IP:$malicious_ip_enforcement_enabled and mode:$malicious_ip_enforcement_mode"
echo -e "Malicious IP Categories:"
for ((i = 0; i < $malicious_ip_enforcement_categories_length; i++))
do
 malicious_ip_enforcement_category=$(cat $file | jq  -r --arg i "$i" ".policy.malicious_ip_enforcement.ip_categories[$i] | join(\", \")")
 IFS=', ' read -r -a array_category_settings <<< "$malicious_ip_enforcement_category"
 category=$(echo "${array_category_settings[2]}" | tr '[:lower:]' '[:upper:]')
 block=${array_category_settings[0]}
 log=${array_category_settings[1]}
 echo -e "$category, block:$block, log:$log"
done
echo -e ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>App Firewall:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
echo -e "High risk attack mitigation:$high_risk_attack_mitigation_enabled and mode:$high_risk_attack_mitigation_enforcement_mode"
echo -e "_______________________________________________________________________________"
echo -e "HTTP compliance enforcement:$http_compliance_enforcement_enabled"
echo -e "_______________________________________________________________________________"
echo -e "Threat_campaigns:$threat_campaigns_enabled and mode:$threat_campaigns_enforcement_mode"
echo -e "_______________________________________________________________________________"
echo -e "Sensitive parameters: $sensitive_parameters_enabled"
echo -e "Parameters List:\r\n$sensitive_parameters_list"
echo -e "XML attributes List:\r\n$sensitive_xml_attributes_list"
echo -e "XML elements List:\r\n$sensitive_xml_elements_list"
echo -e ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Service Policy:<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
echo -e "IP enforcement:$ip_enforcement_enabled"
echo -e "IP addresses:"
for ((i = 0; i < $ip_enforcement_length; i++))
do
 ip_enforcement=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.ip_enforcement.ips[$i] | join(\", \")")
 IFS=', ' read -r -a array_ip_enforcement <<< "$ip_enforcement"
 ip=${array_ip_enforcement[1]}
 action=${array_ip_enforcement[0]}
 log=${array_ip_enforcement[3]}
 description=${array_ip_enforcement[2]}
 echo -e "$ip, action:$action, log:$log, description: $description"
done
echo -e "_______________________________________________________________________________"
echo -e "Geolocation_enforcement:$geolocation_enforcement_enabled"
echo -e "Disallowed countries:"
IFS=', ' read -r -a array_disallowed_countries <<< "$geolocation_disallowed_countries"
for country in "${array_disallowed_countries[@]}"
do
    country_code=$(echo "$country" | tr '[:upper:]' '[:lower:]')
    country_name=$(curl -s https://restcountries.com/v2/alpha/$country_code | jq '.name')
    echo -e "$country_name"
done
echo -e "_______________________________________________________________________________"
echo -e "Disallowed file types:$disallowed_file_types_enabled"
echo -e "File types List:\r\n$disallowed_file_list"
echo -e "_______________________________________________________________________________"
echo -e "Method enforcement:$allowed_methods_enabled"
echo -e "Allowed methods List:\r\n$allowed_methods_list"
echo -e "_______________________________________________________________________________"
echo -e "Exceptions:"
echo -e "Cookies:"
for ((i = 0; i < $exceptions_cookies_length; i++))
do
 cookie=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.cookies[$i].name" | base64 --decode)
 SignatureID=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.cookies[$i].signature_ids | .[]")
 echo -e "name:$cookie, SignatureID:$SignatureID"
done
echo -e "\r\nHTTP compliance:\r\n$exceptions_http_compliance"
echo -e "\r\nExceptions_parameters_objects"
echo -e " - Meta characters parameter name:\r\n$exceptions_parameters_objects_meta_characters_param_name"
echo -e " - Parameters names:"
for ((i = 0; i < $exceptions_parameters_objects_parameter_names_length; i++))
do
 exc_parameter_name=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names[$i].name" | base64 --decode)
 exc_param_value_meta_characters=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names[$i].param_value_meta_characters | join(\", \")")
 AUX_SignatureID=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names[$i].signature_ids | length" )
 if (( $AUX_SignatureID > 0 ));
 then
    exc_SignatureID=$(cat $file | jq  -r --arg i "$i" ".policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names[$i].signature_ids | join(\", \")")
    echo -e "Name:$exc_parameter_name, meta character:$exc_param_value_meta_characters, SignatureID:$exc_SignatureID"
 else
   echo -e "Name:$exc_parameter_name, meta character:$exc_param_value_meta_characters"
 fi
done
echo -e "_______________________________________________________________________________"
echo -e "SignatureIDs:\r"
Aux_SignatureIDs=$(cat $file | jq -r '.policy.high_risk_attack_mitigation.exceptions.parameters_objects.parameter_names | map(select(.signature_ids != null))| sort_by(.signature_ids)[]  | [ .signature_ids]| flatten| .[]')
AUX=$(echo -e $Aux_SignatureIDs > aux.txt)
SignatureIDs=$(cat aux.txt | xargs -n1 | sort | uniq)
echo -e $SignatureIDs
