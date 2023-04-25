#!/usr/local/bin/python3.11
from datetime import datetime
import argparse
import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd 

def get_wideip(bigip,user,password):
    auth = HTTPBasicAuth('{}'.format(user), '{}'.format(password))
    headers = {'Content-Type': "application/json"}
    req_vss = requests.get('https://{}/mgmt/tm/gtm/wideip/a?expandSubcollections=true'.format(bigip), headers=headers, auth=auth, verify=False)
    wideip_info =req_vss.json()
    wideips = wideip_info['items']
    df = pd.DataFrame(columns = ['WideIP', 'Pools', 'Last Resort Pool', 'Pool LB Mode', 'Persistence', 'Persistence TTL', 'Persistence CIDR IPv4', 'Persistence CIDR IPv6', 'iRules'])
    for wideip in wideips:

        ### Processing Pools ###
        try :
            Pools = wideip["pools"]
            PoolList = ""
            for pool in Pools:
                poolName=pool['name']
                poolOrder=pool['order']
                poolRatio=pool['ratio']
                poolInfo=str(poolName + " order: " + str(poolOrder) + " ratio: " + str(poolRatio))
                PoolList += str(poolInfo + "; ")
        except:
            pool = "none"
        ### Processing last resort pool ###
        if wideip['lastResortPool'] :
            lastResortPool = wideip['lastResortPool']
        else :
            lastResortPool = "none"

        ### Processing Persistence parameters###
        PersistenceVAL =wideip['persistence']
        if PersistenceVAL == "disabled" :
            ttlPersistence = 'Not Apply'
            persistCidrIpv4 = 'Not Apply'
            persistCidrIpv6 = 'Not Apply'
        else :
            ttlPersistence = wideip['ttlPersistence']
            persistCidrIpv4 = wideip['persistCidrIpv4']
            persistCidrIpv6 = wideip['persistCidrIpv6']
        
        ### Processing iRules ###
        try :
            iRules = wideip["rules"]
            iRulesList = ""
            for irule in iRules:
                iRulesList += str(irule + ", ")
        except :
            iRulesList = "none"

        ### Formatting wideIP configuration ### 
        tmp = {'WideIP':wideip['name'], 'Pools':PoolList, 'Last Resort Pool': lastResortPool, 'Pool LB Mode':wideip['poolLbMode'], 'Persistence':wideip['persistence'], 'Persistence TTL': ttlPersistence, 'Persistence CIDR IPv4': persistCidrIpv4, 'Persistence CIDR IPv6': persistCidrIpv6, 'iRules':iRulesList}   
        df_dictionary = pd.DataFrame([tmp])
        df = pd.concat([df, df_dictionary], ignore_index=True)
    return df
 

def main():
    currentTime = datetime.now()
    parser = argparse.ArgumentParser(description = "This *Python* script helps to export BIGIP's wideIPs configuration to a CSV file", epilog='The script generates a CSV file named as: WideIPInfo-<hostname>_<date>.csv')    
    parser.add_argument('--bigip', type=str, required=True)
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    args = parser.parse_args()

    wideip = get_wideip(args.bigip, args.user, args.password)
    wideip.to_csv("WideIPInfo-{}_{}.csv".format(args.bigip,currentTime.strftime("%m-%d-%Y")), index = False, sep=',', encoding='utf-8')

if __name__ == "__main__":
   main()
