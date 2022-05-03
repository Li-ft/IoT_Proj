# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 00:20:10 2021

@author: Administrator
"""


from MyMQTT import *
import json
import time
import requests
import sys

class Publisher:
    def __init__(self):
        self.deviceInfo = json.load(open('MotionSensor.json'))
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
                "n": "HumanPresence",
                "v": 0,
                "t": 0,
                "TSwriteApiKey": 0
                    }]
            }
        self.TSwriteApiKey = 0
        self.ChannelID = ""
                
    def start(self):
        self.client.start()
        kitchenInfo = requests.post(self.catelogAddress, json=self.deviceInfo).text
        kitchen = json.loads(kitchenInfo)
        self.topic = kitchen["MotionTopic"]
        self.valveTopic = kitchen["ValveTopic"]
        self.TSwriteApiKey = kitchen["TSwriteApiKey"]
        self.ChannelID = str(kitchen["ChannelID"])
        
    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/device/" + self.deviceID + "/" + self.ChannelID)
    
    def Publish(self, HumanPresenceStatus, nowTime):
        payload = self.payload
        payload["bn"] = self.valveTopic
        payload["e"][0]["t"] = nowTime
        payload["e"][0]["v"] = int(HumanPresenceStatus)
        payload["e"][0]["TSwriteApiKey"] = self.TSwriteApiKey
        self.client.myPublish(self.topic,json.dumps(payload))
        print(json.dumps(payload,indent=4))

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        self.client.myOnConnect(paho_mqtt, userdata, flags, rc)

if __name__ == "__main__":
    HumanPresenceStatus = False #default status is no human presence
    motionSensor = Publisher()
    motionSensor.start()

    print("Motion sensor is running...")
    print("Press 'h' to activate the motion sensor, which means there is human entering or leaving the room")
    print("Press 'q' to quit the motion sensor")
    while (True):
        order = input()
        if order == "h":
            nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            HumanPresenceStatus = bool(1 - HumanPresenceStatus)#For the first trigger, there is human presence
            motionSensor.Publish(HumanPresenceStatus, nowTime)

        elif order == "q":
            break
        else:
            print("Wrong order!")
    motionSensor.stop()
