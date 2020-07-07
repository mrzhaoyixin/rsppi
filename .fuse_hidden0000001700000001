#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,subprocess,re,config,time

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def send_to_onenet(data,id):
    url = "http://api.heclouds.com/devices/"+config.configure_deveice.get("deveiceID")+"/datapoints" 
    headers = {
            "api-key": config.configure_deveice.get("api-key"),
            "Content-type": "application/json"
        }
    params = {
        "datastreams": [
            {
                "id": id,
                "datapoints": [
                    {
                        "value": data
                    }
                ]
            }
        ]
    }
    response = requests.post(url, json=params, headers=headers)
    return response.text

if __name__ == '__main__':
    '''
    print("ping start")
    arglist = sys.argv[1:]
    print("args:",arglist)
    for ip in arglist:
        print(to_json(get_ping_result(ip)))
    '''
