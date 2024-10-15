from datetime import datetime
import argparse
import json
import requests
import pandas as pd 

def get_access_logs(token,tenant,namespace,loadbalancer,hours):

    df = pd.DataFrame(columns = ['Time', 'Request ID', 'Response Code', 'Source IP address', 'Domain' ,'Country', 'City', 'Response Details','Method', 'Request Path'])

    currentTime = datetime.now()
    midTime = int(round(datetime.timestamp(currentTime)))
    startTime = midTime - (hours*3600)
    while True:
        endTime = midTime
        midTime= endTime - (24*3600)
        if hours < 24:
            midTime=startTime
        BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/access_logs'.format(tenant,namespace)
        headers = {'Authorization': "APIToken {}".format(token)}
        auth_response = requests.post(BASE_URL, data=json.dumps({"aggs": {}, "end_time": "{}".format(endTime), "limit": 0, "namespace": "{}".format(namespace), "query": "{{vh_name=\"ves-io-http-loadbalancer-""{}""\"}}".format(loadbalancer), "sort": "DESCENDING", "start_time": "{}".format(midTime),"scroll":True }), headers=headers)
        accessLogs = auth_response.json()
        if 'logs' in accessLogs:
            logs = accessLogs['logs']
        
            for event in logs:
                item_dict = json.loads(event)
                tmp = {'Time':item_dict['time'], 'Request ID':item_dict['req_id'], 'Response Code':item_dict['rsp_code'], 'Source IP address':item_dict['src_ip'],'Domain':item_dict['original_authority'], 'Country':item_dict['country'], 'City':item_dict['city'], 'Response Details':item_dict['rsp_code_details'],'Method':item_dict['method'], 'Request Path':item_dict['req_path']}   
                df_dictionary = pd.DataFrame([tmp])
                df = pd.concat([df, df_dictionary], ignore_index=True)
            while (accessLogs["scroll_id"]!=""):
                BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/access_logs/scroll'.format(tenant,namespace)
                auth_response = requests.post(BASE_URL, data=json.dumps({"namespace": "{}".format(namespace), "scroll_id": "{}".format(accessLogs["scroll_id"])}), headers=headers)
                accessLogs = auth_response.json()
                logs = accessLogs['logs']
                for event in logs:
                    item_dict = json.loads(event)
                    tmp = {'Time':item_dict['time'], 'Request ID':item_dict['req_id'], 'Response Code':item_dict['rsp_code'], 'Source IP address':item_dict['src_ip'],'Domain':item_dict['original_authority'], 'Country':item_dict['country'], 'City':item_dict['city'], 'Response Details':item_dict['rsp_code_details'],'Method':item_dict['method'], 'Request Path':item_dict['req_path']}   
                    df_dictionary = pd.DataFrame([tmp])
                    df = pd.concat([df, df_dictionary], ignore_index=True)
        hours=hours-24
        if hours<24:
            break
       
    return df




def main():
    currentTime = datetime.now()
    parser = argparse.ArgumentParser(description = "This *Python* script helps to export the Access logs from *F5 Distributed Cloud* via the XC API into a CSV file.", epilog='The script generates a CSV file named as: xc-access_logs-<TENANT>_<NAMESPACE>-<date>.csv')    
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--tenant', type=str, required=True)
    parser.add_argument('--namespace', type=str, required=True)
    parser.add_argument('--loadbalancer', type=str, required=True)
    parser.add_argument('--hours', type=int, required=True)
    args = parser.parse_args()

    security_logs = get_access_logs(args.token,args.tenant,args.namespace,args.loadbalancer,args.hours)
    security_logs.to_csv("f5-xc-access_logs-{}_{}-{}.csv".format(args.tenant,args.namespace,currentTime.strftime("%m-%d-%Y")), index = False, sep=',', encoding='utf-8')


if __name__ == "__main__":
   main()
