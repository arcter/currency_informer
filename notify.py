#!/usr/bin/env python3

import configparser
import json
import requests
import notify2
import logging
import time
baseURL='https://v6.exchangerate-api.com/v6/'
endpoint='/latest/'
    

def init_config(config_file):
    config=configparser.RawConfigParser()
    config.read(config_file)
    api_key=config['exchange-rates']['apikey']
    currency=config['exchange-rates']['currency'].upper()
    thresholds=config['exchange-rates']['threasholdfile']
    return api_key,currency,thresholds

notify2.init("News Notifier")



if __name__ == "__main__":
    api_key,currency,threshold_file=init_config('api.conf')
    req=requests.get(baseURL+api_key+endpoint+currency)
    logging.basicConfig(level=logging.INFO)
    logging.info(req.status_code)
    if req.status_code != 200:
        logging.fatal("Problem with API.")
        noti = notify2.Notification(None)
        noti.update("FATAL","Fatal problem with API connection")
        noti.timeout=5000
        noti.show()
        quit(-1)
    rates_json = req.json()
    try:
        f=open(threshold_file)
        thresholds=json.load(f)
    except:
        logging.fatal("Error loading threasholds.")
        noti = notify2.Notification(None)
        noti.update("FATAL","Fatal problem with loading threasholds")
        noti.timeout=5000
        noti.show()
        quit(-1)
    for threshold in thresholds:
        if threshold in rates_json['conversion_rates']:
            if thresholds[threshold] > rates_json['conversion_rates'][threshold]:
                logging.info("send notification about exchange rates")
                noti = notify2.Notification(None)
                noti.update("EXCHANGE","Exchange rate is low for: "+str(threshold))
                noti.timeout=5000
                noti.show()
        else:
            print("Not in")
        print(threshold)
    time.sleep(60*60)
