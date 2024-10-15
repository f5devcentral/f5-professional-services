from datetime import datetime
import argparse
import json
import requests
import pandas as pd 

def get_securiy_logs(token,tenant,namespace,loadbalancer,hours):

    df = pd.DataFrame(columns = ['Time', 'Request ID', 'Event Type', 'Source IP address', 'X-Forwarded-For' ,'Country', 'City', 'Browser', 'Domain','Method', 'Request Path', 'Response Code'])

    currentTime = datetime.now()
    midTime = int(round(datetime.timestamp(currentTime)))
    startTime = midTime - (hours*3600)

    while True:
        endTime = midTime
        midTime= endTime - (24*3600)
        if hours < 24:
            midTime=startTime
        BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/app_security/events'.format(tenant,namespace)
        headers = {'Authorization': "APIToken {}".format(token)}
        auth_response = requests.post(BASE_URL, data=json.dumps({"aggs": {}, "end_time": "{}".format(endTime), "limit": 0, "namespace": "{}".format(namespace), "query": "{{vh_name=\"ves-io-http-loadbalancer-""{}""\"}}".format(loadbalancer), "sort": "DESCENDING", "start_time": "{}".format(midTime), "scroll":True } ), headers=headers)
        securityLogs = auth_response.json()
        events = securityLogs['events']
        if 'events' in securityLogs:
            
            for event in events:
                item_dict = json.loads(event)
                tmp = {'Time':item_dict['time'], 'Request ID':item_dict['req_id'], 'Event Type':item_dict['sec_event_name'], 'Source IP address':item_dict['src_ip'],'X-Forwarded-For':item_dict['x_forwarded_for'], 'Country':item_dict['country'], 'City':item_dict['city'], 'Browser':item_dict['browser_type'], 'Domain':item_dict['domain'],'Method':item_dict['method'], 'Request Path':item_dict['req_path'], 'Response Code':item_dict['rsp_code']}   
                df_dictionary = pd.DataFrame([tmp])
                df = pd.concat([df, df_dictionary], ignore_index=True)
            while (securityLogs["scroll_id"]!=""):
                BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/app_security/events/scroll'.format(tenant,namespace)
                auth_response = requests.post(BASE_URL, data=json.dumps({"namespace": "{}".format(namespace), "scroll_id": "{}".format(securityLogs["scroll_id"]),"scroll":True}), headers=headers)
                securityLogs = auth_response.json()
                events = securityLogs['events']
                for event in events:
                    item_dict = json.loads(event)
                    tmp = {'Time':item_dict['time'], 'Request ID':item_dict['req_id'], 'Event Type':item_dict['sec_event_name'], 'Source IP address':item_dict['src_ip'],'X-Forwarded-For':item_dict['x_forwarded_for'], 'Country':item_dict['country'], 'City':item_dict['city'], 'Browser':item_dict['browser_type'], 'Domain':item_dict['domain'],'Method':item_dict['method'], 'Request Path':item_dict['req_path'], 'Response Code':item_dict['rsp_code']}   
                    df_dictionary = pd.DataFrame([tmp])
                    df = pd.concat([df, df_dictionary], ignore_index=True)
        hours=hours-24
        if hours<24:
            break
        
    return df


def main():
    currentTime = datetime.now()
    parser = argparse.ArgumentParser(description = "This *Python* script helps to export the Security Events logs from *F5 Distributed Cloud* via the XC API into a CSV file.", epilog='The script generates a CSV file named as: xc-security_events-<TENANT>_<NAMESPACE>-<date>.csv')    
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--tenant', type=str, required=True)
    parser.add_argument('--namespace', type=str, required=True)
    parser.add_argument('--loadbalancer', type=str, required=True)
    parser.add_argument('--hours', type=int, required=True)
    args = parser.parse_args()

    security_logs = get_securiy_logs(args.token,args.tenant,args.namespace,args.loadbalancer,args.hours)
    security_logs.to_csv("f5-xc-security_events-{}_{}-{}.csv".format(args.tenant,args.namespace,currentTime.strftime("%m-%d-%Y")), index = False, sep=',', encoding='utf-8')


if __name__ == "__main__":
   main()
