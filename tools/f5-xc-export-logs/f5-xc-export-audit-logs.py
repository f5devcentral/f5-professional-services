from datetime import datetime
import argparse
import json
import requests
import pandas as pd

def logs_processor(logs, df):
    for event in logs:
        event_dict = json.loads(event)
        time = ''
        user = ''
        namespace = ''
        method = ''
        requestPath = ''
        message = ''
        for key in event_dict:
            if key == 'time':
                time = event_dict[key]
            if key == 'user':
                user = event_dict[key]
            if key == 'namespace':
                namespace = event_dict[key]
            if key == 'method':
                method = event_dict[key]
            if key == 'req_path':
                requestPath = event_dict[key].split('?')[0]
            if key.endswith('user_message'):
                message = event_dict[key]
        tmp = {'Time':time, 'User':user, 'Namespace':namespace, 'Method':method, 'Request Path':requestPath, 'Message':message}
        df_dictionary = pd.DataFrame([tmp])
        df = pd.concat([df, df_dictionary], ignore_index=True)
    return df

def get_audit_logs(token,tenant,namespace,hours):
    df = pd.DataFrame(columns = ['Time', 'User', 'Namespace', 'Method', 'Request Path', 'Message'])
    currentTime = datetime.now()
    midTime = int(round(datetime.timestamp(currentTime)))
    startTime = midTime - (hours*3600)
    while True:
        endTime = midTime
        midTime = endTime - (24*3600)
        if hours < 24:
            midTime=startTime
        BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/audit_logs'.format(tenant,namespace)
        headers = {'Authorization': "APIToken {}".format(token)}
        auth_response = requests.post(BASE_URL, data=json.dumps({"aggs": {}, "end_time": "{}".format(endTime), "limit": 0, "namespace": "{}".format(namespace), "sort": "DESCENDING", "start_time": "{}".format(midTime),"scroll":True }), headers=headers)
        auditLogs = auth_response.json()
        if 'logs' in auditLogs:
            df = logs_processor(auditLogs['logs'], df)
            while (auditLogs["scroll_id"]!=""):
                BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/audit_logs/scroll'.format(tenant,namespace)
                auth_response = requests.post(BASE_URL, data=json.dumps({"namespace": "{}".format(namespace), "scroll_id": "{}".format(auditLogs["scroll_id"])}), headers=headers)
                auditLogs = auth_response.json()
                if 'logs' in auditLogs:
                    df = logs_processor(auditLogs['logs'], df)
        hours=hours-24
        if hours<24:
            break
    return df

def main():
    parser = argparse.ArgumentParser(description = "This *Python* script exports audit logs from *F5 Distributed Cloud* via the XC API into a CSV file.", epilog='The script generates a CSV file named: f5-xc-audit_logs-<TENANT>_<NAMESPACE>-<date>.csv')
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--tenant', type=str, required=True)
    parser.add_argument('--namespace', type=str, required=True)
    parser.add_argument('--hours', type=int, required=True)
    args = parser.parse_args()
    currentTime = datetime.now()
    auditLogsCSV = get_audit_logs(args.token,args.tenant,args.namespace,args.hours)
    auditLogsCSV.to_csv("f5-xc-audit_logs-{}_{}-{}.csv".format(args.tenant,args.namespace,currentTime.strftime("%m-%d-%Y")), index = False, sep=',', encoding='utf-8')

if __name__ == "__main__":
   main()