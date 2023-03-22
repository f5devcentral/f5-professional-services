import getpass
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def connection():
    print("#######################################################################")
    url = 'https://' + device + '/mgmt/shared/authn/login'
    user = input("Username: ")
    pw = getpass.getpass('Enter your password: ')
    data = {"username": user, "password": pw, "loginProviderName": "tmos"}
    r = requests.post(url, json=data, verify=False)
    validation(r)
    token(r)

def validation(r):
    if 'commandResult' in r.json():
        print("Request was successfull but with command errors")
        print(r.json()['commandResult'])
        quit()
    elif r.status_code == 200:
        print ("Request was succesful!!!", r)
        exit
    else:
        print("Oops!! something was wrong ",r.text)
        quit("Aborting...")

def token(r):
    print("#######################################################################")
    print("Requesting token ")
    validation(r)
    token = r.json()['token']['token']
    h = {'X-F5-Auth-Token': token}
    vslist(h)

def vslist(h):
    url = 'https://' + device + '/mgmt/tm/ltm/virtual'
    r = requests.get(url, headers=h, verify=False)
    print("#######################################################################")
    print("Requesting list of Virtual servers")
    validation(r)
    v = r.json()
    checkForPolicy(v,h)
    for vs in v['items']:
        virtual = vs['name']
        asmpolicy(virtual,h)

def asmpolicy(virtual,h):
    asmp="asm_policy_VS_" + virtual
    ltmp="ltm_policy_VS_"+ virtual
    url = 'https://' + device + '/mgmt/tm/util/bash/'
    data = [{"utilCmdArgs": "-c \"tmsh create asm policy " + asmp + " parent-policy " + asmParent + "\"", "command": "run"},
            {"utilCmdArgs": "-c \"tmsh create ltm policy " + ltmDraft + ltmp + " requires add { http tcp } controls add { asm } strategy first-match rules add { default { actions add { 1 { asm enable policy " + asmp + " }}}}\"","command": "run"},
            {"utilCmdArgs": "-c \"tmsh publish ltm policy " + ltmDraft + ltmp + "\"", "command": "run"},
            {"utilCmdArgs": "-c \"tmsh modify ltm virtual " + virtual + " profiles add { websecurity } policies add { " + ltmp + " }\"","command": "run"}]
    print("#######################################################################")
    print("Creating ASM policy and attaching it to the Virtual Server", virtual)
    for task in range(len(data)):
        r = requests.post(url, headers=h, verify=False, json=data[task])
        validation(r)

def delprof(virtual,h):
    url = 'https://' + device + '/mgmt/tm/ltm/virtual/' + virtual + '/profiles'
    r = requests.get(url, headers=h, verify=False)
    validation(r)
    sp = r.json()
    for prof in sp['items']:
        pname = prof['name']
        if pname == "websecurity":
            delprof = 'https://' + device + '/mgmt/tm/ltm/virtual/' + virtual + '/profiles/' + pname + '/'
            r = requests.delete(delprof, headers=h, verify=False)
            print("Policy removed from VS",virtual,r)

def checkForPolicy(v,h):
    for vs in v['items']:
        virtual = vs['name']
        url = 'https://' + device + '/mgmt/tm/ltm/virtual/' + virtual + '/policies'
        r = requests.get(url, headers=h, verify=False)
        print("#######################################################################")
        print("Checking for policies on VS " + virtual + "....")
        validation(r)
        p = r.json()
        for pol in p['items']:
            policy = pol['name']
            print("Removing Policy", policy)
            delurl = 'https://' + device + '/mgmt/tm/ltm/virtual/' + virtual + '/policies/' + policy + '/'
            r = requests.delete(delurl, headers=h, verify=False)
            delprof(virtual, h)
            print("#######################################################################")

device = "big-ip-301x-bigip1.fcruz" # Your BIG-IP FQDN or IP address
ltmDraft = "Drafts/"
asmParent = "Drafts" # Here you should relpace "Drafts" with the name of the Parent ASM policy 
connection()
