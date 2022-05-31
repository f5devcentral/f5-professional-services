import requests
import json
import urllib3
import argparse
import sys

if sys.version_info < (3, 5):
    print('Please upgrade your Python version to 3.5 or higher')
    sys.exit(1)

def export_awaf_policies(device,username,password,format,output):

    if not(format == "xml" or format == "json" or format == "plc"):
        print("ERROR: invalid format specified", file=sys.stderr)
        sys.exit(1)

    session = requests.Session()
    session.verify=False
    session.auth = (username,password)
  
    #get all awaf policies
    try:
        req = session.get("https://%s/mgmt/tm/asm/policies?$select=name,id,fullPath,link" % device)
        req.raise_for_status()
    except requests.exceptions.RequestException as error:
        print("ERROR: %s" % error, file=sys.stderr)
        sys.exit(1)

    awaf_policies = req.json()['items']

    for policy in awaf_policies:

        filename = policy['fullPath'][1:].replace("/","-") + "." + format

        data = {}
        data['filename'] = filename

        if format == "plc":
            data['format'] = "binary"
        else:
            data['format'] = format

        data['policyReference'] = {}
        data['policyReference']['link'] = policy['selfLink']

        #export awaf policy
        try:
            req = session.post("https://%s/mgmt/tm/asm/tasks/export-policy" % device, json=data)
            req.raise_for_status()
        except requests.exceptions.RequestException as error:
            print("ERROR: %s" % error, file=sys.stderr)
            sys.exit(1)

        task_link = req.json()['selfLink'].replace("localhost",device)

        #wait for the export task finished
        while True:

            try:
                req = session.get(task_link)
                req.raise_for_status()
            except requests.exceptions.RequestException as error:
                print("ERROR: %s" % error, file=sys.stderr)
                sys.exit(1)

            task_status = req.json()['status']

            if task_status == "COMPLETED":
                task_message = req.json()['result']['message']
                break

        #if the policy was successfully exported, save in the file
        if "was successfully exported" in task_message:

            try:
                req = session.get("https://%s/mgmt/tm/asm/file-transfer/downloads/%s" % (device,filename))
                req.raise_for_status()
            except requests.exceptions.RequestException as error:
                print("ERROR: %s" % error, file=sys.stderr)
                sys.exit(1)

            filepath = "%s/%s" % (output,filename)

            if format == "json" or format == "xml":
                exportedPolicy = open(filepath, "w")
            else:
                exportedPolicy = open(filepath, "wb")

            if format == "json":
                exportedPolicy.write(json.dumps(req.json(), indent=2, sort_keys=True))
            elif format == "xml":
                exportedPolicy.write(str(req.text))
            else:
                exportedPolicy.write(req.content)

            exportedPolicy.close()

            print("AWAF Policy %s saved to file %s." % (policy["fullPath"], filepath))
        else:
            print("ERROR: failed to export AWAF Policy %s" % policy["fullPath"], file=sys.stderr)

            

def main():
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser(description = 'A small script to export all AWAF policies from a BIG-IP device.')

    parser.add_argument('--device', '-d', type=str, required=True)
    parser.add_argument('--username', '-u', type=str, required=True)
    parser.add_argument('--password', '-p', type=str, required=True)
    parser.add_argument('--format', '-f', type=str, required=False, default="xml", choices=['json','xml','plc'])
    parser.add_argument('--output', '-o', type=str, required=False, default=".")

    args = parser.parse_args()

    export_awaf_policies(args.device,args.username,args.password,args.format,args.output)

if __name__ == "__main__":
   main()
