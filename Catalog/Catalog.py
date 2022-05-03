# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 14:44:24 2021

@author: Administrator
"""


import cherrypy
import json
import time
import os
from KitchenGenerator import *
import sys
sys.path.append("..")
from ThingSpeak.Thingspeak import Thingspeak


class Catalog(object):
    exposed=True
    def __init__(self):
        #I store the devices and services in 2 seperate json files
        self._Device = open('device.json')
        self.Device = json.load(self._Device)
        self.DeviceList = self.Device['deviceList']
        self._Service = open('service.json')
        self.Service = json.load(self._Service)
        self.ServiceList = self.Service['serviceList']
        self.ServiceConfig = json.load(open('ServiceConfig.json'))
        self.Broker = json.load(open('broker.json'))
        self._Kitchen = open('kitchen.json')
        self.Kitchen = json.load(self._Kitchen)
        self.KitchenList = self.Kitchen['kitchenList']
        self.KitGen = KitchenGenerator()
        self.TSinfo = json.load(open("thingspeakConfig.json"))
        self.TS = Thingspeak(self.TSinfo)
        self.TelegramConfig = json.load(open('TelegramConfig.json'))
        
    def GET(self, *uri, **params):
        devicelist = self.DeviceList
        servicelist = self.ServiceList
        kitchenList = self.KitchenList
        broker = [self.Broker]
        devicewithID = []
        servicewithID = []
        kitchenwithID = []
        List = []

        
        if len(uri)!=0:            
            if uri[0] == "broker":
                brokerDict = {"Brokers in the catalog":self.Broker}
                jsonResult = json.dumps(brokerDict, indent=4)
            elif uri[0] == "all":
                List.append(devicelist)
                List.append(servicelist)
                List.append(kitchenList)
                List.append(broker)
                jsonResult = json.dumps(List, indent=4)
            elif uri[0] == "device":
                if "id" in params:
                    IDdevice = params["id"]
                    for device in self.DeviceList:
                        if "deviceID" in device:
                            if device["deviceID"] == IDdevice:
                                devicewithID.append(device)
                            else:
                                pass
                        else:
                            pass
                        deviceDict = {f"Device with ID {IDdevice}":devicewithID}
                        jsonResult = json.dumps(deviceDict, indent=4)
                else:
                    jsonResult = json.dumps(self.DeviceList, indent=4)
            elif uri[0] == "service":
                if "id" in params:
                    IDservice = params["id"]
                    for service in self.ServiceList:
                        if "serviceID" in service:
                            if service["serviceID"] == IDservice:
                                servicewithID.append(service)
                            else:
                                pass
                        else:
                            pass
                        serviceDict = {f"Service with ID {IDservice}":servicewithID}
                        jsonResult = json.dumps(serviceDict, indent=4)
                else:
                    jsonResult = json.dumps(self.ServiceList, indent=4)
            elif uri[0] == "kitchen":
                if "id" in params:
                    KitchenNum = params["id"]
                    for kitchen in self.KitchenList:
                        if "kitchenNumber" in kitchen:
                            if kitchen["kitchenNumber"] == KitchenNum:
                                kitchenwithID.append(kitchen)
                            else:
                                pass
                        else:
                            pass
                        KitchenDict = {f"Kitchen of Number {KitchenNum}":kitchenwithID}
                        jsonResult = json.dumps(KitchenDict, indent=4)
                else:
                    jsonResult = json.dumps(self.KitchenList, indent=4)                    
            else:
                m = {"GET":"URI", 
                     "broker":"Available message broker in the platform", 
                     "all":"All the registered devices",
                     "device with id params":"A specific device with a deviceID",
                     "service with id params":"A specific service with a serviceID",
                     "POST":"URI",
                     "add":"Add a new device",
                     "update":"Update the information of a device"}
                jsonResult = json.dumps(m, indent=4)
                #print instructions if there is no uri or wrong uri
        else:
            m = {"GET":"URI", 
                 "broker":"Available message broker in the platform", 
                 "all":"All the registered devices",
                 "device with id params":"A specific device with a deviceID",
                 "service with id params":"A specific service with a serviceID",
                 "POST":"URI",
                 "add":"Add a new device",
                 "update":"Update the information of a device"}
            jsonResult = json.dumps(m, indent=4)
            
        return jsonResult
    
    def POST(self):        
        body = cherrypy.request.body.read()
        new = json.loads(body)
        insertTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        new['insert-timestamp'] = insertTime
        NewKitchen = None
        updated = 0
        kitchenExisted = 0
        
        if new['registerType'] == "device":
            if self.DeviceList == []:
                self.DeviceList.append(new)
                NewKitchen = self.KitGen.Generator(new["deviceID"])
                updated = 1
            else:
                for i in range(len(self.DeviceList)):
                    #if the new device already exists in the list
                    #it means the device might offline due to unexpected reason
                    #then update the registion
                    if self.DeviceList[i]["deviceID"] == new["deviceID"]:
                        self.DeviceList[i] = new
                        updated = 1
                    else:
                        pass
                pass
            if updated == 0:
                self.DeviceList.append(new)
                NewKitchen = self.KitGen.Generator(new["deviceID"])
            
            self.Device['deviceList'] = self.DeviceList
            self._Device.close()
            DeviceNew = open('device.json', 'w')
            DeviceNew.write(json.dumps(self.Device))
            DeviceNew.close()
            self._Device = open('device.json')
            self.Device = json.load(self._Device)
            self.DeviceList = self.Device['deviceList']

            if self.KitchenList == []:
                self.KitchenList.append(NewKitchen)
                kitchenExisted = 1
            else:
                for i in range(len(self.KitchenList)):
                    #check if the new kitchen already exists in the list
                    if self.KitchenList[i]["kitchenNumber"] == NewKitchen["kitchenNumber"]:
                        kitchenExisted = 1
                    else:
                        pass
                pass
            if kitchenExisted == 0:
                self.KitchenList.append(NewKitchen)
            
            if new["deviceType"] == "Sensor":
                clientID = new["deviceName"]
                resource = new["available-resources"]
                TSwriteApiKey, ChannelID = self.TS.CreateChannel(clientID, resource)
                NewKitchen["TSwriteApiKey"] = TSwriteApiKey
                NewKitchen["ChannelID"] = ChannelID
            return json.dumps(NewKitchen)
        
        elif new['registerType'] == "service":
            if self.ServiceList == []:
                self.ServiceList.append(new)
                updated = 1
            else:
                for i in range(len(self.ServiceList)):
                    if self.ServiceList[i]["serviceID"] == new["serviceID"]:
                        self.ServiceList[i] = new
                        updated = 1
                    else:
                        pass
                pass
            if updated == 0:
                self.ServiceList.append(new)

            self.Service['serviceList'] = self.ServiceList
            self._Service.close()
            ServiceNew = open('service.json', 'w')
            ServiceNew.write(json.dumps(self.Service))
            ServiceNew.close()
            self._Service = open('service.json')
            self.Service = json.load(self._Service)
            self.ServiceList = self.Service['serviceList']
            
            return json.dumps(self.ServiceConfig)
        
        else:
            m = {"ERROR":"Register Type is not recongized."}
            
            return json.dumps(m)
    
    def DELETE(self, *uri):
        if uri[0] == "device":
            for device in self.DeviceList:
                if device["deviceID"] == uri[1]:
                    if len(uri)>2:
                        self.TS.DeleteChannel(uri[2])
                    self.DeviceList.remove(device)
                    self.Device['deviceList'] = self.DeviceList
                    self._Device.close()
                    DeviceNew = open('device.json', 'w')
                    DeviceNew.write(json.dumps(self.Device))
                    DeviceNew.close()
                    break
        elif uri[0] == "service":
            for service in self.ServiceList:
                if service["serviceID"] == uri[1]:
                    self.ServiceList.remove(service)
                    self.Service['serviceList'] = self.ServiceList
                    self._Service.close()
                    ServiceNew = open('service.json', 'w')
                    ServiceNew.write(json.dumps(self.Service))
                    ServiceNew.close()
                    break
            pass
        else:
            pass
                
    
if __name__=="__main__":
    #Standard configuration to serve the url "localhost:8090"

    conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True,
                'tools.staticdir.root':os.path.abspath(os.getcwd())
        },
    }
    cherrypy.config.update({'server.socket_port':8090})
    cherrypy.quickstart(Catalog(),'/',conf)
