# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 00:20:10 2021

@author: Administrator
"""


from MyMQTT import *
import json
import time
import requests
import random
import sys

class Publisher():    
    def __init__(self):
        self.deviceInfo = json.load(open('TempSensor.json'))
        self.catelogAddress = self.deviceInfo["CatelogAddress"]
        self.deviceID = self.deviceInfo["deviceID"]
        self.resource = self.deviceInfo["available-resources"]
        brokerInformation = requests.get(self.deviceInfo["brokerInquiry"]).json()
        brokerInfo = brokerInformation["Brokers in the catalog"]
        broker = brokerInfo["broker"]
        port = int(brokerInfo["port"])
        self.clientID = self.deviceInfo["deviceName"]
        self.client = MyMQTT(self.clientID,broker,port,None)
        self.topic = ""
        self.valveTopic = ""        
        self.payload = {
            "bn": "",
            "e": [{
                "id": self.deviceID,
                "n": "temperature",
                "u": "Cel",
                "t": 0,
                "v": 0,
                "TSwriteApiKey": 0
                    }]
            }
        self.TSwriteApiKey = 0
        self.ChannelID = ""
        
    def start(self):
        self.client.start()
        kitchenInfo = requests.post(self.catelogAddress, json=self.deviceInfo).text
        kitchen = json.loads(kitchenInfo)
        self.topic = kitchen["TempTopic"]
        self.valveTopic = kitchen["ValveTopic"]
        self.TSwriteApiKey = kitchen["TSwriteApiKey"]
        self.ChannelID = str(kitchen["ChannelID"])
        
    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/device/" + self.deviceID + "/" + self.ChannelID)
        
    
    def Publish(self, measurement, nowTime):
        payload = self.payload
        payload["bn"] = self.valveTopic
        payload["e"][0]["t"] = nowTime
        payload["e"][0]["v"] = measurement
        payload["e"][0]["TSwriteApiKey"] = self.TSwriteApiKey
        self.client.myPublish(self.topic,json.dumps(payload))
        print(json.dumps(payload,indent=4))

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        self.client.myOnConnect(paho_mqtt, userdata, flags, rc)



if __name__ == "__main__":

    tempSensor = Publisher()
    tempSensor.start()

    print("Temperature sensor is running...")
    print("Enter 'q' to exit")
    while (True):
        measurement = random.uniform(80, 120)
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        tempSensor.Publish(measurement, nowTime)

        if input() == 'q':
            break
        else:
            pass
    tempSensor.stop()
