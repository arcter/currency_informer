#!/usr/bin/env python3

import logging
from logging.handlers import SysLogHandler
import time
import notify2
from service import find_syslog, Service
import configparser
import json
import requests

baseURL='https://v6.exchangerate-api.com/v6/'
endpoint='/latest/'

def init_config(config_file):
    config=configparser.RawConfigParser()
    config.read(config_file)
    api_key=config['exchange-rates']['apikey']
    currency=config['exchange-rates']['currency'].upper()
    thresholds=config['exchange-rates']['threasholdfile']
    return api_key,currency,thresholds


class MyService(Service):
    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)
        self.logger.addHandler(SysLogHandler(address=find_syslog(),
                               facility=SysLogHandler.LOG_DAEMON))
        self.logger.setLevel(logging.INFO)

    def run(self):
        while not self.got_sigterm():
            api_key,currency,threshold_file=init_config('/etc/currency_informer/api.conf')
            req=requests.get(baseURL+api_key+endpoint+currency)
            self.logger.info(req.status_code)
            if req.status_code != 200:
                self.logger.fatal("Problem with API.")
                noti = notify2.Notification(None)
                noti.update("FATAL","Fatal problem with API connection",icon="/etc/currency_informer/money.png")
                noti.timeout=5000
                noti.show()
                quit(-1)
            rates_json = req.json()
            try:
                f=open(threshold_file)
                thresholds=json.load(f)
            except:
                self.logger.fatal("Error loading threasholds.")
                noti = notify2.Notification(None)
                noti.update("FATAL","Fatal problem with loading threasholds",icon="/etc/currency_informer/money.png")
                noti.timeout=5000
                noti.show()
                quit(-1)
            for threshold in thresholds:
                if threshold in rates_json['conversion_rates']:
                    if thresholds[threshold] > rates_json['conversion_rates'][threshold]:
                        self.logger.info("send notification about exchange rates")
                        noti = notify2.Notification(None)
                        noti.update("EXCHANGE","Exchange rate is low for: "+str(threshold),icon="/etc/currency_informer/money.png")
                        noti.timeout=5000
                        noti.show()
                else:
                    print("Not in")
                print(threshold)
            time.sleep(60*60)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = MyService('my_service', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)
