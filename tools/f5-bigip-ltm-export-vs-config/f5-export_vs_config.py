from datetime import datetime
import argparse
import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd 

def get_vss(bigip,user,password):
    auth = HTTPBasicAuth('{}'.format(user), '{}'.format(password))
    headers = {'Content-Type': "application/json"}
    req_vss = requests.get('https://{}/mgmt/tm/ltm/virtual?expandSubcollections=true'.format(bigip), headers=headers, auth=auth, verify=False)
    vss_info =req_vss.json()
    vss = vss_info['items']
    df = pd.DataFrame(columns = ['Virtual Server', 'Source', 'Destination', 'Pool', 'Profiles', 'SNAT', 'Persistence', 'Fallback Persistence', 'iRule', 'Traffic Polices'])
    for vs in vss:
        ### Processing Pools ###
        try :
            pool = vs['pool']
        except:
            pool = "none"

        ### Processing Profiles ###
        Profiles =vs['profilesReference']['items']
        ProfileList=""
        for profile in Profiles:
             ProfileList += str(profile['name'] + ", ")

        ### Processing SNATs ###
        SNAT =vs['sourceAddressTranslation']['type']
        if SNAT != "snat":
           snat=vs['sourceAddressTranslation']['type']
        else:
            snat=vs['sourceAddressTranslation']['pool']

        ### Processing Persistence Profiles ###
        try :
            persistence = vs['persist'][0]['name']
        except:
            persistence = "none"

        ### Processing Fallback Persistence Profiles ###
        try :
            fallbackpersistence = vs["fallbackPersistence"]
        except:
            fallbackpersistence = "none"

        ### Processing iRules ###
        try :
            iRules = vs["rules"]
            iRulesList = ""
            for irule in iRules:
                iRulesList += str(irule + ", ")
        except :
            iRulesList = "none"

        ### Processing Traffic Policies ###
        try :
            Policies =vs['policiesReference']['items']
            PoliciesList=""
            for policy in Policies:
                 PoliciesList += str(policy['name'] + ", ")
        except:
            PoliciesList = "none"

        ### Formatting virtual server configuration ###
        tmp = {'Virtual Server':vs['name'], 'Source': vs['source'], 'Destination':vs['destination'], 'Pool':pool, 'Profiles':ProfileList, 'SNAT':snat, 'Persistence':persistence, 'Fallback Persistence': fallbackpersistence, 'iRule':iRulesList, 'Traffic Polices':PoliciesList}   
        df_dictionary = pd.DataFrame([tmp])
        df = pd.concat([df, df_dictionary], ignore_index=True)
    return df
 

def main():
    currentTime = datetime.now()
    parser = argparse.ArgumentParser(description = "This *Python* script helps to export BIGIP's virtual server configuration to a CSV file.", epilog='The script generates a CSV file named as: VSInfo-<hostname>_<date>.csv')    
    parser.add_argument('--bigip', type=str, required=True)
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    args = parser.parse_args()

    vs = get_vss(args.bigip, args.user, args.password)
    vs.to_csv("VSInfo-{}_{}.csv".format(args.bigip,currentTime.strftime("%m-%d-%Y")), index = False, sep=',', encoding='utf-8')

if __name__ == "__main__":
   main()
