import argparse
import csv
import datetime
import getpass
import json
import os
import re
import requests
import urllib3

# global variable - file to save data
dt = datetime.datetime.today()
filename = "asm-policies-qk-%02d-%02d-%02d-%02d%02d.csv" %(dt.month,dt.day,dt.year,dt.hour,dt.minute)
path = "data"
filename = os.path.join("data", filename)
device = ""

def get_token(b, url_base, creds):
    url_auth = '%s/shared/authn/login' % url_base
    try:
        payload = {}
        payload['username'] = creds[0]
        payload['password'] = creds[1]
        payload['loginProviderName'] = 'tmos'
        token = b.post(url_auth, json.dumps(payload)).json()['token']['token']
    except:
        token = '' 
    return token

def audit_asm_policies_high_level(device,token):

    print('Working on ASM policies for device %s' % device)
 
    # filter policies - obtains policy ID, name, enforcement mode, has parent, type and parent policy name
    url_base_asm = 'https://%s/mgmt/tm/asm/policies/?$select=id,name,enforcementMode,hasParent,type,parentPolicyName' % device
    bigip = requests.session()
    bigip.headers.update({'Content-Type': 'application/json'})
    bigip.headers.update({'X-F5-Auth-Token': token})
    bigip.verify = False
    bigip.auth = None
    
    r = bigip.get(url_base_asm)
    json_data = r.json()

    # iterate over the data obtained and performed specific policy lookup (e.g. how many signatures are in staging)
    for i in json_data['items']:
        if( i['type']=='parent'):
            continue
        if( i['hasParent'] == False):
            i['parentPolicyName'] = 'N/A'
        policies_data = [ device, i['name'], i['enforcementMode'], i['hasParent'], i['parentPolicyName']]
        policy_data = audit_asm_policy_high_level(device,i['id'],token)
        policies_data = policies_data + policy_data 
        asm_policy_high_level_save(policies_data)

def audit_asm_policy_high_level(device, policy_id, token):

    # filter data specific for each policy 
    url_sig_tot = 'https://%s/mgmt/tm/asm/policies/%s/signatures?$top=1&$select=totalItems' % (device,policy_id)
    url_sig_sta = 'https://%s/mgmt/tm/asm/policies/%s/signatures?$filter=performStaging+eq+true&$top=1&$select=totalItems' % (device,policy_id)
    url_par_sta = 'https://%s/mgmt/tm/asm/policies/%s/parameters?$filter=performStaging+eq+true&$top=1&$select=totalItems' % (device,policy_id)
    url_url_sta = 'https://%s/mgmt/tm/asm/policies/%s/urls?$filter=performStaging+eq+true&$top=1&$select=totalItems' % (device, policy_id)
    url_sig_ready = 'https://%s/mgmt/tm/asm/policies/%s/signatures?$filter=hasSuggestions+eq+false+AND+wasUpdatedWithinEnforcementReadinessPeriod+eq+false+and+performStaging+eq+true&$top=1' % (device,policy_id)
    url_sug = 'https://%s/mgmt/tm/asm/policies/%s/suggestions?$top=1&$select=totalItems' % (device, policy_id)
    url_learn = 'https://%s/mgmt/tm/asm/policies/%s/policy-builder?$select=learningMode' % (device, policy_id)


    bigip = requests.session()
    bigip.headers.update({'Content-Type': 'application/json'})
    bigip.headers.update({'X-F5-Auth-Token': token})
    bigip.verify = False
    bigip.auth = None

    policy_data = []

    # learning mode
    r = bigip.get(url_learn)
    policy_data.append(r.json()['learningMode'])   

    # total signatures in staging, parameters, URL and signatures ready to be enforce
    r = bigip.get(url_sig_tot)
    policy_data.append(r.json()['totalItems'])
    
    r = bigip.get(url_sig_sta)
    policy_data.append(r.json()['totalItems'])
    
    r = bigip.get(url_sig_ready)
    policy_data.append(r.json()['totalItems'])
    
    r = bigip.get(url_par_sta)
    policy_data.append(r.json()['totalItems'])
    
    r = bigip.get(url_url_sta)
    policy_data.append(r.json()['totalItems'])

    r = bigip.get(url_sug)
    policy_data.append(r.json()['totalItems'])

    return policy_data

def asm_policy_high_level_save(data):

    # create file if it does not exist
    if(os.path.isfile(filename)==False):
        headers = ['device','policy', 'enforcement mode','has parent','parent policy','learning mode', 'tot sig', 'sig in stg','sig ready', 'params in stg','urls in stg', 'total suggestions']
        with open(filename, mode='w') as pol_file:
            pol_file = csv.writer(pol_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            pol_file.writerow(headers)
    
    with open(filename, mode='a') as pol_file:
        pol_file = csv.writer(pol_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        pol_file.writerow(data)

def check_active(device,token):
    
    # obtain device name
    url_base_asm = 'https://%s/mgmt/tm/sys/global-settings?$select=hostname' % device
    bigip = requests.session()
    bigip.headers.update({'Content-Type': 'application/json'})
    bigip.headers.update({'X-F5-Auth-Token': token})
    bigip.verify = False
    bigip.auth = None
    
    r = bigip.get(url_base_asm)
    hostname = r.json()['hostname']
 
    # filter policies - obtains policy ID, name, enforcement mode, has parent, type and parent policy name
    url_base_asm = 'https://%s/mgmt/tm/cm/traffic-group/traffic-group-1/stats?$select=deviceName,failoverState' % device
    bigip = requests.session()
    bigip.headers.update({'Content-Type': 'application/json'})
    bigip.headers.update({'X-F5-Auth-Token': token})
    bigip.verify = False
    bigip.auth = None
    
    r = bigip.get(url_base_asm)
    json_data = r.json()
    
    for i in json_data['entries']:
        devices = json_data['entries'][i]['nestedStats']
        # returns similar to 
        #{'entries': {'deviceName': {'description': '/Common/bigip1.f5labs.net'}, 'failoverState': {'description': 'standby'}}}
        device = devices['entries']['deviceName']['description']
        state = devices['entries']['failoverState']['description']
        
        if (hostname in device) and ('active' in state):
            return True
         
    return False

def main():
    urllib3.disable_warnings()

    parser = argparse.ArgumentParser()

    parser.add_argument("device", help='a file containing list of BIG-IP devices separated by line, e.g. devices.txt')
    args = vars(parser.parse_args())

    device = args['device']

    username = input('Enter your username: ') 
    password = getpass.getpass('Enter your password:')

    try:
      with open(device,'r') as a_file:
          for line in a_file:
              device = line.strip()
              # TODO - test connectivity with each device and report on the ones failing 
              url_base = 'https://%s/mgmt' % device
              bigip = requests.session()
              bigip.headers.update({'Content-Type': 'application/json'})
              bigip.auth = (username, password)
              bigip.verify = False
              token = get_token(bigip, url_base, (username, password))
              print(device)
              if (not token):
                  print('Unable to obtain token for device ' + device)
                  continue 
              if not check_active(device, token): 
                  print('Device ' + device + ' is not active, skipping it...')
                  continue
              audit_asm_policies_high_level(device,token)
      print('File saved: %s' % filename)
    except:
      print('Error reading file %s' % device)

