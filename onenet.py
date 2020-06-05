#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests,config
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
