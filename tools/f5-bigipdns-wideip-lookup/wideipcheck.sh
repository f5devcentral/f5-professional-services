#!/bin/bash
#Script that will pull wide-ip names from a BIGIP-DNS device (using iControl Rest), the #perform a (dig) Lookup on each name.

password="L4BP4ss!"
results=""$1"_results_`date +%m%d%y`.txt"


 
if [ "$#" -ne 3 ]
    then
        echo -e "Usage:\n wideipcheck.sh <GTM address> <Listener address> <Username>\n"
       
    else
        echo -e "Enter Password:"
        read -s password
        curl -sku "$3":"$password" -X GET https://"$1"/mgmt/tm/gtm/wideip/a | jq . -M|grep -i '"name"' |awk -F: '{print $2}' |uniq |sed 's/[\"\,]//g' > .wideips.txt
         
        count=`cat .wideips.txt |wc -l`
        echo -e "\nThere are "$count" wide-ips in your configuration. \n"
        echo -e "Lookups starting...\n"
		
		file=".wideips.txt"
		lines=$(cat $file)
 
        for line in $lines
		do
		  lookup=`dig +timeout=1 +retry=0 "$line" +short @"$2"` 
		  if [ "$lookup" == "" ]
		    then 
			  lookup=" *** No response ***"
			  echo "$line $lookup" >> "$results"
			else
			  echo "$line  $lookup" >> "$results"
			fi
		done
			
		echo -e "\nLookups complete.\n"
		echo -e "\nResults\n"
		cat "$results"
		 
        rm -f .wideips.txt
fi
