# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 16:45:30 2021

@author: Administrator
"""


from MyMQTT import *
import json
import time
import requests

class Subscriber():
    def __init__(self):
        self.log = {}
        self.measu = []
        self.measure = []
        self.overThres = {}
        self.valveStatus = True
        self.deviceInfo = json.load(open('ValveDevice.json'))
        self.catelogAddress = self.deviceInfo["CatelogAddress"]
        self.deviceID = self.deviceInfo["deviceID"]
        brokerInformation = requests.get(self.deviceInfo["brokerInquiry"]).json()
        brokerInfo = brokerInformation["Brokers in the catalog"]
        broker = brokerInfo["broker"]
        port = int(brokerInfo["port"])
        clientID = self.deviceInfo["deviceName"]
        self.client = MyMQTT(clientID,broker,port,self)
        self.valveTopic = ""
        self.noderedTopic = ""

    
    def start(self):
        self.client.start()
        kitchenInfo = requests.post(self.catelogAddress, json=self.deviceInfo).text
        kitchen = json.loads(kitchenInfo)
        self.valveTopic = kitchen["ValveTopic"]
        self.noderedTopic = kitchen["noderedTopic"]
        self.client.mySubscribe(self.valveTopic)

    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/device/" + self.deviceID)

    def notify(self, valveTopic, msg):
        payload=json.loads(msg)
        if payload["e"][0]["n"] == "temperature":
            print(json.dumps(payload ,indent=4))
            print("Danger message received.")
            self.valveStatus = False
            if self.valveStatus:
                print(f"The valve is turned on")
            else:
                print(f"The valve is turned off")
                telegramMSG = {
                    "bnn": self.valveTopic,
                    "e": [{
                        "id": self.deviceID,
                        "n": "teleswitch",
                        "v": int(self.valveStatus)
                           }]
                    }
                self.client.myPublish(self.valveTopic, json.dumps(telegramMSG))
        elif payload["e"][0]["n"] == "switch":
            self.valveStatus = bool(payload["e"][0]["v"])
            if self.valveStatus:
                print(f"The valve is turned on")
            else:
                print(f"The valve is turned off")
        else:
            pass
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        noderedMSG = {
            "bn": self.noderedTopic,
            "e": [{
                "id": self.deviceID,
                "n": "Valve Status",
                "t": nowTime,
                "v": int(self.valveStatus)
                    }]
            }
        self.client.myPublish(self.noderedTopic, json.dumps(noderedMSG))

        
        if self.log:
            #非空
            self.measu.append(payload["e"][0])
            self.log["e"] = self.measu
            
        else:
            #空
            self.log = payload
            self.measu = payload["e"]
        
        catalogNew = open('danger_log.json', 'w')
        catalogNew.write(json.dumps(self.log))
        catalogNew.close()
        


if __name__=="__main__":
    """
    device = open('ValveDevice.json')
    deviceInfo = json.load(device)
    brokerInquiry = deviceInfo["brokerInquiry"]
    r = requests.get(brokerInquiry)
    print(json.dumps(r.json(),indent=4))
    brokerInformation = r.json()
    brokerInfo = brokerInformation["Brokers in the catalog"]
    broker = brokerInfo["broker"]
    port = int(brokerInfo["port"])
    clientID = deviceInfo["deviceName"]
    SubTopic = deviceInfo["SubTopic"]
    noderedTopic = deviceInfo["noderedTopic"]
    deviceID = deviceInfo["deviceID"]
    catelogAddress = deviceInfo["CatelogAddress"]
    """
    Valve = Subscriber()
    Valve.start()
    
    print("Gas Valve is running...")
    print("Enter 'q' to exit")
    while (True):
        if input() == 'q':
            break
        else:
            pass
    Valve.stop()
    
