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
        self.serviceInfo = json.load(open('GasCtrlService.json'))
        self.catelogAddress = self.serviceInfo["CatelogAddress"]
        brokerInformation = requests.get(self.serviceInfo["brokerInquiry"]).json()
        brokerInfo = brokerInformation["Brokers in the catalog"]
        broker = brokerInfo["broker"]
        port = int(brokerInfo["port"])
        clientID = self.serviceInfo["serviceName"]
        self.client = MyMQTT(clientID,broker,port,self)
        self.SubTopic = ""
        self.serviceID = self.serviceInfo["serviceID"]
        self.logTemperature = []
        self.overThres = []
        self.measureTemperature = []
        self.measureTempOverThres = []
        self.measureMotion = []
        self.HumanpresenceList = []
        
    def start(self):
        self.client.start()
        conf = requests.post(self.catelogAddress, json=self.serviceInfo).text
        config = json.loads(conf)
        self.SubTopic = config["SubTopic"]
        self.client.mySubscribe(self.SubTopic)
        

    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/service/" + self.serviceID)
                       
    def notify(self, SubTopic, msg):
        payload=json.loads(msg)
        print("The received message is...")
        print(json.dumps(payload ,indent=4))
        valveTopic = payload["bn"]
        updated = 0
        overupdated = 0
        
        #收到的msg是HumanPresence
        if payload["e"][0]["n"] == "HumanPresence":
            if self.HumanpresenceList:
                #非空
                for HL in self.HumanpresenceList:
                    if HL["valveTopic"] == valveTopic:
                        HL["Humanpresence"] = bool(payload["e"][0]["v"])
                        print(self.HumanpresenceList)
                        updated = 1
                    else:
                        pass
                if updated == 0:
                    HumanpresenceStatus = {"valveTopic":valveTopic,
                                           "Humanpresence":bool(payload["e"][0]["v"])}
                    self.HumanpresenceList.append(HumanpresenceStatus)
                    print(self.HumanpresenceList)
                    updated = 1
            else:
                #空
                HumanpresenceStatus = {"valveTopic":valveTopic,
                                       "Humanpresence":bool(payload["e"][0]["v"])}
                self.HumanpresenceList.append(HumanpresenceStatus)
                print(self.HumanpresenceList)
                updated = 1

        #收到的msg是Temperature
        elif payload["e"][0]["n"] == "temperature":
            if self.logTemperature:
                #非空
                for LT in self.logTemperature:
                    if LT["bn"] == valveTopic:
                        LT["e"].append(payload["e"][0])
                        updated = 1
                    else:
                        pass
                if updated == 0:
                    self.logTemperature.append(payload)
                    updated = 1
            else:
                #空
                self.logTemperature.append(payload)
                updated = 1

            
            catalogNew = open('temp_log.json', 'w')
            catalogNew.write(json.dumps(self.logTemperature))
            catalogNew.close()
            
            if payload["e"][0]["v"] > 100:
                if self.HumanpresenceList:
                    #非空
                    if [L for L in self.HumanpresenceList if valveTopic in L.values()]:                        
                        for HL in self.HumanpresenceList:                            
                            if HL["valveTopic"] == valveTopic:
                                if HL["Humanpresence"] == False:
                                    print(valveTopic)
                                    self.client.myPublish(valveTopic, json.dumps(payload))
                                    print("Danger message published.")
                                else:
                                    print("Danger message not published.")
                            else:
                                pass
                    else: #If there is no matching valveTopic in the list, it means there is an alarm,
                          #but there is no corresponding motion sensor online, so we send the alarm anyway.
                        print(valveTopic)
                        self.client.myPublish(valveTopic, json.dumps(payload))
                        print("Danger message published.")

                else:
                    #空
                    print(valveTopic)
                    self.client.myPublish(valveTopic, json.dumps(payload))
                    print("Danger message published.")
                                    
                if self.overThres:
                    #非空
                    for OT in self.overThres:
                        if OT["bn"] == valveTopic:
                            OT["e"].append(payload["e"][0])
                            overupdated = 1
                        else:
                            pass
                    if overupdated == 0:
                        self.overThres.append(payload)
                        overupdated = 1
                else:
                    #空
                    self.overThres.append(payload)
                    overupdated = 1
            
                catalogNew = open('overThreshold.json', 'w')
                catalogNew.write(json.dumps(self.overThres))
                catalogNew.close()
            else:
                pass
        else:
            pass
        
        
        


if __name__=="__main__":
    GasCtrl = Subscriber()
    GasCtrl.start()
    
    print("Gas Control Service is running...")
    print("Enter 'q' to exit")
    while (True):
        if input() == 'q':
            break
        else:
            pass
    GasCtrl.stop()
    
