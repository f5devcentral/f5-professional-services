#!/usr/local/bin/python3.11
from datetime import datetime
import argparse
import json
import requests
import pandas as pd 

def get_securiy_logs(token,tenant,namespace,hours):
    currentTime = datetime.now()
    endTime = int(round(datetime.timestamp(currentTime)))
    startTime = endTime - (hours*3600)
    BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/app_security/events'.format(tenant,namespace)
    headers = {'Authorization': "APIToken {}".format(token)}
    auth_response = requests.post(BASE_URL, data=json.dumps({"aggs": {}, "end_time": "{}".format(endTime), "limit": 0, "namespace": "m-alvarado", "query": "{vh_name=\"ves-io-http-loadbalancer-m-alvarado-lb\"}", "sort": "DESCENDING", "start_time": "{}".format(startTime) }), headers=headers)

    securityLogs = auth_response.json()
    events = securityLogs['events']
    df = pd.DataFrame(columns = ['Time', 'Request ID', 'Event Type', 'Source IP address', 'X-Forwarded-For' ,'Country', 'City', 'Browser', 'Domain','Method', 'Request Path', 'Response Code'])
    for event in events:
        item_dict = json.loads(event)
        tmp = {'Time':item_dict['time'], 'Request ID':item_dict['req_id'], 'Event Type':item_dict['sec_event_name'], 'Source IP address':item_dict['src_ip'],'X-Forwarded-For':item_dict['x_forwarded_for'], 'Country':item_dict['country'], 'City':item_dict['city'], 'Browser':item_dict['browser_type'], 'Domain':item_dict['domain'],'Method':item_dict['method'], 'Request Path':item_dict['req_path'], 'Response Code':item_dict['rsp_code']}   
        df_dictionary = pd.DataFrame([tmp])
        df = pd.concat([df, df_dictionary], ignore_index=True)
    return df


def main():
    currentTime = datetime.now()
    parser = argparse.ArgumentParser(description = "Script to get F5 XC security events from the last X hours and export them to a CSV file", epilog='The scripts save F5 XC security events to a CSV file named: security_events-<TENANT>-<NAMESPACE>_<date>-<hour>')    
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--tenant', type=str, required=True)
    parser.add_argument('--namespace', type=str, required=True)
    parser.add_argument('--hours', type=int, required=True)
    args = parser.parse_args()

    security_logs = get_securiy_logs(args.token,args.tenant,args.namespace,args.hours)
    security_logs.to_csv("security_events-{}-{}_{}.csv".format(args.tenant,args.namespace,currentTime.strftime("%m-%d-%Y_%H:%M")), index = False, sep=',', encoding='utf-8')


if __name__ == "__main__":
   main()
