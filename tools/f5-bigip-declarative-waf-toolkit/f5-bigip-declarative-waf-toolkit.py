import requests
import json
import logging
import urllib3
import time
import os
import argparse
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]: %(message)s'
)

logger = logging.getLogger(__name__)

class AWAF:

    _base_url                   = None
    _session                    = None
    _waf_policies               = None

    _export_waf_policy_data     = None
    _export_waf_policy_fullpath = None
    _export_waf_policy_filename = None

    _export_waf_suggestions_data     = None

    _import_waf_policy_data     = None
    _import_waf_policy_json     = None
    _import_waf_policy_len      = None
    _import_waf_policy_fullpath = None
    _import_waf_policy_filename = None

    def __init__(self,device,username,password) -> None:
        
        self._base_url = f"https://{device}"

        self._session = requests.Session()
        self._session.verify = False
        self._session.auth = (username,password)

    def _get_waf_policies(self) -> int:

        logger.debug("Retrieving WAF policies.")

        url = f"{self._base_url}/mgmt/tm/asm/policies?$select=name,id,fullPath,link"

        try:
            r = self._session.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1
        
        json_resp = json.loads(r.text)        
        
        policies = json_resp['items']

        self._waf_policies = {}
        
        for p in policies:
            policy = {}
            policy['id'] = p['id'] 
            self._waf_policies[p['fullPath']] = policy

        logger.debug("WAF policies successfully retrieved.")

        return 0

    def _print_waf_policies(self) -> int:

        if self._waf_policies == None:
            logger.error("No WAF policies found.")
            return 1

        for idx, policy in enumerate(self._waf_policies):
            print(f"{idx+1}: {policy} ({self._waf_policies[policy]['id']})")

        return 0

    def _export_waf_policy(self,policy,export_mode) -> int:

        if self._waf_policies == None:
            logger.error("No WAF policies found.")
            return 1

        if policy not in self._waf_policies:
            logger.error(f"WAF Policy {policy} not found.")
            return 1
        
        policy_id = self._waf_policies[policy]['id']
        filename = policy[1:].replace("/","-") + "." + "json"

        logger.debug(f"Running a 'export-policy' task.")

        url = f"{self._base_url}/mgmt/tm/asm/tasks/export-policy"

        data = {}
        data['filename'] = filename
        data['format'] = "json"
        data['policyReference'] = {}
        data['policyReference']['link'] = f"https://localhost/mgmt/tm/asm/policies/{policy_id}"
        if export_mode == "full":
            data['minimal'] = False
        else:
            data['minimal'] = True

        try:
            r = self._session.post(url,json=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1
        
        json_resp = json.loads(r.text)

        logger.debug("Waiting for the 'export-policy' task to complete.")

        task_id = json_resp['id']
        url = f"{self._base_url}/mgmt/tm/asm/tasks/export-policy/{task_id}"
        
        task_status = None
        for i in range(300):

            try:
                r = self._session.get(url)
                r.raise_for_status()
            except requests.exceptions.RequestException as error:
                logger.error(error)
                return 1

            task_status = json.loads(r.text)['status']

            if task_status == "COMPLETED":
                break

            time.sleep(1)

        if task_status != "COMPLETED":
            logger.error(f"The 'export-policy' task failed or timed out.")
            return 1

        logger.debug(f"The 'export-policy' task completed successfully.")

        self._export_waf_policy_filename = filename
        self._export_waf_policy_fullpath = policy

        return 0

    def _download_waf_policy(self) -> int:
        
        if self._waf_policies == None:
            logger.error("No WAF policies found.")
            return 1
        
        if self._export_waf_policy_filename == None:
            logger.error("No WAF policy available for download.")

        logger.debug(f"Downloading the exported WAF policy.")

        url = f"{self._base_url}/mgmt/tm/asm/file-transfer/downloads/{self._export_waf_policy_filename}"

        try:
            r = self._session.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1

        json_resp = json.loads(r.text)

        self._export_waf_policy_data = json_resp

        logger.debug(f"WAF Policy successfully downloaded.")

        return 0

    def _save_waf_policy(self,output) -> int:

        if self._export_waf_policy_data == None:
            logger.error("WAF Policy data not found.")
            return 1

        logger.debug(f"Saving WAF policy to file.")

        try:
            with open(output,"w") as myfile:
                myfile.write(json.dumps(self._export_waf_policy_data, indent=2, sort_keys=True))
        except Exception as error:
            logger.error(error)
            return 1

        logger.debug(f"WAF Policy sucessfully saved to file.")

        return 0

    def _export_waf_suggestions(self,policy) -> int:

        if self._waf_policies == None:
            logger.error("No WAF policies found.")
            return 1
        
        if policy not in self._waf_policies:
            logger.error(f"WAF Policy {policy} not found.")
            return 1
        
        policy_id = self._waf_policies[policy]['id']

        data = {}
        data['inline'] = True
        data['policyReference'] = {}
        data['policyReference']['link'] = f"https://localhost/mgmt/tm/asm/policies/{policy_id}"

        logger.debug("Running a 'export-suggestions' task.")

        url = f"{self._base_url}/mgmt/tm/asm/tasks/export-suggestions"
        
        try:
            r = self._session.post(url, json=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1

        json_resp = json.loads(r.text)

        logger.debug("Waiting for the 'export-suggestions' task to complete.")

        task_id = json_resp['id']
        url = f"{self._base_url}/mgmt/tm/asm/tasks/export-suggestions/{task_id}"

        task_status = None
        for i in range(300):

            try:
                r = self._session.get(url)
                r.raise_for_status()
            except requests.exceptions.RequestException as error:
                logger.debug(r.text)
                logger.error(error)
                return 1

            json_resp = json.loads(r.text)
            task_status = json_resp['status']

            if task_status == "COMPLETED":
                break

            time.sleep(1)

        if task_status != "COMPLETED":
            logger.error(f"Failed to export the learning suggestions for the policy {policy}.")
            return 1

        self._export_waf_suggestions_data = json_resp['result']

        logger.debug(f"The 'export-suggestions' task completed successfully.")

        return 0

    def _save_waf_suggestions(self,output) -> int:

        if self._export_waf_suggestions_data == None:
            logger.error("No WAF suggestions data found.")
            return 1
        try:
            with open(output,"w") as myfile:
                myfile.write(json.dumps(self._export_waf_suggestions_data, indent=2, sort_keys=True))    
        except Exception as error:
            logger.error(error)
            return 1

        return 0

    def _build_waf_policy(self,policy,policy_file,suggestions_file) -> int:
        
        logger.debug("Building WAF policy.")

        try:
            with open(policy_file, 'r') as file:
                waf_policy_data = json.load(file)
        except Exception as error:
            logger.debug(error)
            logger.error(f"Failed to load the WAF policy file '{policy_file}'.")
            return 1

        if suggestions_file != None:

            try:
                with open(suggestions_file, 'r') as file:
                    waf_suggestions_data = json.load(file)
            except Exception as error:
                logger.debug(error)
                logger.error(f"Failed to load the WAF suggestions file '{suggestions_file}'.")
                return 1
        else:
            waf_suggestions_data = None

        if waf_suggestions_data != None:
            if 'suggestions' in waf_suggestions_data:
                logger.debug("Merging suggestions with the WAF policy.")
                waf_policy_data['modifications'] = waf_suggestions_data['suggestions']

        waf_policy_data['policy']['fullPath'] = policy

        self._import_waf_policy_data = waf_policy_data
        self._import_waf_policy_json = json.dumps(waf_policy_data)
        self._import_waf_policy_len = len(self._import_waf_policy_json)
        self._import_waf_policy_fullpath = waf_policy_data['policy']['fullPath']
        self._import_waf_policy_filename =  os.path.basename(policy_file)

        logger.debug("WAF policy successfully built.")

        return 0
    
    def _upload_waf_policy(self) -> int:

        if self._import_waf_policy_data == None:
            logger.error("WAF Policy data not found.")
            return 1

        logger.debug("Uploading WAF policy.")

        url = f"{self._base_url}/mgmt/tm/asm/file-transfer/uploads/{self._import_waf_policy_filename}"

        headers = {}
        headers['Content-Range'] = f"0-{self._import_waf_policy_len-1}/{self._import_waf_policy_len}"

        try:
            r = self._session.post(url, data=self._import_waf_policy_json, headers=headers)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1
        
        logger.debug("WAF policy sucessfully uploaded.")

        return 0

    def _import_waf_policy(self) -> int:

        if self._import_waf_policy_data == None:
            logger.error("WAF Policy data not found.")
            return 1

        logger.debug(f"Running a 'import-policy' task.")
    
        url = f"{self._base_url}/mgmt/tm/asm/tasks/import-policy/"

        data = {}
        data['filename'] = self._import_waf_policy_filename
        data['policy'] = {}
        data['policy']['fullPath'] = self._import_waf_policy_fullpath

        try:
            r = self._session.post(url, json=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1

        json_resp = json.loads(r.text)

        logger.debug("Waiting for the 'import-policy' task to complete.")

        task_id = json_resp['id']
        url = f"{self._base_url}/mgmt/tm/asm/tasks/import-policy/{task_id}"
        
        task_status = None
        for i in range(300):

            try:
                r = self._session.get(url)
                r.raise_for_status()
            except requests.exceptions.RequestException as error:
                logger.debug(r.text)
                logger.error(error)
                return 1

            task_status = json.loads(r.text)['status']

            if task_status == "COMPLETED":
                break

            time.sleep(1)

        if task_status != "COMPLETED":
            logger.error("The 'import-policy' task failed or timed out.")

        logger.debug("The 'import-policy' task completed successfully.")
        
        return 0

    def _apply_waf_policy(self) -> int:

        logger.debug("Running a 'apply-policy' task.")

        url = f"{self._base_url}/mgmt/tm/asm/tasks/apply-policy/"

        data = {}
        data['policy'] = {}
        data['policy']['fullPath'] = self._import_waf_policy_fullpath

        try:
            r = self._session.post(url, json=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logger.error(error)
            return 1
        
        json_resp = json.loads(r.text)

        logger.debug("Waiting for the 'apply-policy' task to complete.")

        task_id = json_resp['id']
        url = f"{self._base_url}/mgmt/tm/asm/tasks/apply-policy/{task_id}"

        task_status = None
        for i in range(300):

            try:
                r = self._session.get(url)
                r.raise_for_status()
            except requests.exceptions.RequestException as error:
                logger.debug(r.text)
                logger.error(error)
                return 1

            task_status = json.loads(r.text)['status']

            if task_status == "COMPLETED":
                break

            time.sleep(1)

        if task_status != "COMPLETED":
            logger.debug("The 'apply-policy' task failed or timed out.")
            return 1

        logger.debug("WAF Policy successfully applied.")

        return 0

    def _export_waf_policy_cleanup(self) -> None:
        
        self._export_waf_policy_data = None
        self._export_waf_policy_fullpath = None
        self._export_waf_policy_filename = None

    def _export_waf_suggestions_cleanup(self) -> None:

        self._export_waf_suggestions_data = None

    def _import_waf_policy_cleanup(self) ->None:

        self._import_waf_policy_data     = None
        self._import_waf_policy_json     = None
        self._import_waf_policy_len      = None
        self._import_waf_policy_fullpath = None
        self._import_waf_policy_filename = None

    def _export_all_waf_policies(self,directory,export_mode) -> int:

        if self._waf_policies == None:
            logger.error("No WAF policies found.")
            return 1

        for policy in self._waf_policies:
            
            output = f"{directory}/{policy[1:].replace('/','_')}.json"
            
            logger.info(f"Exporting WAF policy '{policy}' to the file '{output}'.")
        
            ret = self._export_waf_policy(policy,export_mode)
            if ret != 0:
                logger.error(f"Failed to export the WAF policy.")
                return ret

            ret = self._download_waf_policy()
            if ret != 0:
                logger.error(f"Failed to export the WAF policy.")
                return ret

            ret = self._save_waf_policy(output)
            if ret != 0:
                logger.error(f"Failed to export the WAF policy.")
                return ret

            self._export_waf_policy_cleanup()

            logger.info(f"WAF policy successfully exported.")
            
        return 0

    def list_waf_policies(self) -> int:

        ret = self._get_waf_policies()
        if ret != 0:
            return ret
        
        ret = self._print_waf_policies()
        if ret != 0:
            return ret
        
        return 0

    def export_waf_policy(self,policy,output,export_mode) -> int:

        logger.info(f"Exporting WAF policy '{policy}' to the file '{output}'.")

        ret = self._get_waf_policies()
        if ret != 0:
            logger.error("Failed to export the WAF policy.")
            return ret
        
        ret = self._export_waf_policy(policy,export_mode)
        if ret != 0:
            logger.error("Failed to export the WAF policy.")
            return ret

        ret = self._download_waf_policy()
        if ret != 0:
            logger.error("Failed to export the WAF policy.")
            return ret

        ret = self._save_waf_policy(output)
        if ret != 0:
            logger.error("Failed to export the WAF policy.")
            return ret

        self._export_waf_policy_cleanup()

        logger.info("WAF policy successfully exported.")

        return 0

    def export_waf_suggestions(self,policy,output) -> int:
        
        logger.info(f"Exporting learning suggestions for the policy '{policy}' to the file '{output}'.")

        ret = self._get_waf_policies()
        if ret != 0:
            logger.error("Failed to export the learning suggestions.")
            return ret

        ret = self._export_waf_suggestions(policy)
        if ret != 0:
            logger.error("Failed to export the learning suggestions.")
            return ret
        
        ret = self._save_waf_suggestions(output)
        if ret != 0:
            logger.error("Failed to export the learning suggestions.")
            return ret

        self._export_waf_suggestions_cleanup()

        logger.info("Learning suggestions successfully exported.")

        return 0

    def import_waf_policy(self,policy,policy_file,suggestions_file=None) -> int:

        if suggestions_file:
            logger.info(f"Importing WAF policy '{policy}' from file '{policy_file}' with suggestions from '{suggestions_file}'.")
        else:
            logger.info(f"Importing WAF policy '{policy}' from file '{policy_file}' (no suggestions).")

        ret = self._build_waf_policy(policy,policy_file,suggestions_file)
        if ret != 0:
            return ret

        ret = self._upload_waf_policy()
        if ret != 0:
            return ret
        
        ret = self._import_waf_policy()
        if ret != 0:
            return ret
        
        ret = self._apply_waf_policy()
        if ret != 0:
            return ret

        self._import_waf_policy_cleanup()

        if suggestions_file:
            logger.info("WAF Policy successfully imported (suggestions applied).")
        else:
            logger.info("WAF Policy successfully imported (no suggestions).")

        return 0

    def export_all_waf_policies(self,directory,export_mode) -> int:

        ret = self._get_waf_policies()
        if ret != 0:
            logger.error("Failed to export all WAF policies.")
            return ret
        
        ret = self._export_all_waf_policies(directory,export_mode)
        if ret != 0:
            logger.error("Failed to export all WAF policies.")
            return ret
        
        return 0

def validate_args(parser):
    
    args = parser.parse_args()

    if args.action == "list-waf-policies":

        if args.policy:
            parser.error("Command-line option --policy MUST NOT be used with '--action list-waf-policies'.")

        if args.output:
            parser.error("Command-line option --output MUST NOT be used with '--action list-waf-policies'.")

        if args.policy_file:
            parser.error("Command-line option --policy-file MUST NOT be used with '--action list-waf-policies'.")

        if args.suggestions_file:
            parser.error("Command-line option --suggestions-file MUST NOT be used with '--action list-waf-policies'.")

        if args.export_mode:
            parser.error("Command-line option --export-mode MUST NOT be used with '--action list-waf-policies'.")

    elif args.action in ["export-waf-policy","export-waf-suggestions"]:

        if not args.policy:
            parser.error(f"Command-line option --policy MUST be provided with '--action {args.action}'.")

        if not args.output:
            parser.error(f"Command-line option --output MUST be provided with '--action {args.action}'.")

        if args.policy_file:
            parser.error(f"Command-line option --policy-file MUST NOT be used with '--action {args.action}'.")

        if args.suggestions_file:
            parser.error(f"Command-line option --suggestions-file MUST NOT be used with '--action {args.action}'.")

        if args.action == "export-waf-suggestions":

            if args.export_mode:
                parser.error(f"Command-line option --export-mode MUST NOT be used with '--action {args.action}'.")

    elif args.action == "import-waf-policy":

        if not args.policy:
            parser.error(f"Command-line option --policy MUST be provided with '--action import-waf-policy'.")

        if args.output:
            parser.error(f"Command-line option --output MUST NOT be provided with '--action import-waf-policy'.")

        if not args.policy_file:
            parser.error(f"Command-line option --policy-file MUST be used with '--action import-waf-policy'.")

        if args.export_mode:
            parser.error(f"Command-line option --export-mode MUST NOT be provided with '--action import-waf-policy'.")

    elif args.action == "export-all-waf-policies":

        if args.policy:
            parser.error(f"Command-line option --policy MUST NOT be provided with '--action export-all-waf-policies'.")

        if args.output:
            parser.error(f"Command-line option --output MUST NOT be provided with '--action export-all-waf-policies'.")

        if args.policy_file:
            parser.error(f"Command-line option --policy-file MUST NOT be used with '--action export-all-waf-policies'.")

        if args.suggestions_file:
            parser.error(f"Command-line option --suggestions-file MUST NOT be used with '--action export-all-waf-policies'.")

        if not args.directory:
            parser.error(f"Command-line option --directory MUST be provided with '--action export-all-waf-policies'.")

def main():
    
    parser = argparse.ArgumentParser(description = 'Python script to manage declarative WAF policies (including suggestions).')

    parser.add_argument('--device', type=str, required=True)
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    parser.add_argument('--action', type=str, required=False, default="list-waf-policies", choices=[
        'list-waf-policies','export-waf-policy','export-waf-suggestions','import-waf-policy','export-all-waf-policies'])
    
    parser.add_argument('--policy', type=str, required=False, default=None)
    parser.add_argument('--output', type=str, required=False)
    parser.add_argument('--policy-file', type=str, required=False)
    parser.add_argument('--suggestions-file', type=str, required=False, default=None)
    parser.add_argument('--log-level', type=str, required=False, default="info", choices=['info','debug'])
    parser.add_argument('--export-mode', type=str, required=False, default=None, choices=['minimal','full'])
    parser.add_argument('--directory', type=str, required=False, default=None)

    validate_args(parser)

    args = parser.parse_args()

    device = args.device
    username = args.username
    password = args.password
    action = args.action
    policy = args.policy
    output = args.output
    policy_file = args.policy_file
    suggestions_file = args.suggestions_file
    log_level = args.log_level
    export_mode = args.export_mode
    directory = args.directory

    if export_mode == None:
        export_mode = "minimal"

    # configuring the appropriate log level for the script and the 'requests' and 'urllib3' libraries
    logger.setLevel(log_level.upper())
    logging.getLogger("requests").setLevel(log_level.upper())
    logging.getLogger("urllib3").setLevel(log_level.upper())

    awaf = AWAF(device,username,password)

    if action == "list-waf-policies":
        ret = awaf.list_waf_policies()
    
    elif action == "export-waf-policy":
        ret = awaf.export_waf_policy(policy,output,export_mode)

    elif action =="export-waf-suggestions":
        ret = awaf.export_waf_suggestions(policy,output)
    
    elif action =="import-waf-policy":
        ret = awaf.import_waf_policy(policy,policy_file,suggestions_file=suggestions_file)

    elif action =="export-all-waf-policies":
        ret = awaf.export_all_waf_policies(directory,export_mode)

    sys.exit(ret)

if __name__ == "__main__":
   main()
