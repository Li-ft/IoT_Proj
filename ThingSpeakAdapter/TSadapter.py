# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 17:58:40 2022

@author: Alex Xie
"""

from MyMQTT import *
import json
import time
import requests
import sys
sys.path.append("..")
from ThingSpeak.Thingspeak import Thingspeak

class TS:
    def __init__(self):
        self.serviceInfo = json.load(open('TSadapterService.json'))
        self.catelogAddress = self.serviceInfo["CatelogAddress"]
        brokerInformation = requests.get(self.serviceInfo["brokerInquiry"]).json()
        brokerInfo = brokerInformation["Brokers in the catalog"]
        broker = brokerInfo["broker"]
        port = int(brokerInfo["port"])
        clientID = self.serviceInfo["serviceName"]
        self.client = MyMQTT(clientID,broker,port,self)
        self.SubTopic = ""
        self.serviceID = self.serviceInfo["serviceID"]
        self.TSconfig = ""

        
    def start(self):
        self.client.start()
        conf = requests.post(self.catelogAddress, json=self.serviceInfo).text
        self.TSconfig = json.loads(conf)
        self.SubTopic = self.TSconfig["SubTopic"]
        self.TS = Thingspeak(self.TSconfig)
        self.client.mySubscribe(self.SubTopic)
        

    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/service/" + self.serviceID)
                       
    def notify(self, SubTopic, msg):
        payload=json.loads(msg)
        print("The received message is...")
        print(json.dumps(payload ,indent=4))
        TSwriteApiKey = payload["e"][0]["TSwriteApiKey"]
        measurement = payload["e"][0]["v"]
        self.TS.Update(TSwriteApiKey, measurement)
        
if __name__=="__main__":
    TSadapter = TS()
    TSadapter.start()
    
    print("Thingspeak Adapter is running...")
    print("Enter 'q' to exit")
    while (True):
        if input() == 'q':
            break
        else:
            pass
    TSadapter.stop()
