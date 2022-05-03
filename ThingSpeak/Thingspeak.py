# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 22:49:19 2022

@author: Alex Xie
"""
import json
import requests

class Thingspeak():
    def __init__(self, TSconfig):
        TSinfo = TSconfig
        self.TSURL = TSinfo["TSURL"]
        self.TSupdateURL = TSinfo["TSupdateURL"]
        self.TSuserApiKey = TSinfo["user_api_key"]
        self.API_keyDict = {"api_key": self.TSuserApiKey}
        self.ChannelInfo = {}
        
    def CreateChannel(self, clientID, resource):
        TScreateChannelInfo = {
                "api_key": self.TSuserApiKey,
                "name": clientID,
                "field1": resource,
                "public_flag": True
            }
        TScreateChannel = requests.post(self.TSURL + '.json', data = TScreateChannelInfo).text
        self.ChannelInfo = json.loads(TScreateChannel)
        if "api_keys" in self.ChannelInfo:
            TSwriteApiK = self.ChannelInfo["api_keys"]
            ChannelID = self.ChannelInfo['id']
            for apik in TSwriteApiK:
                if apik["write_flag"] == True:
                    TSwriteApiKey = apik["api_key"]
            print("Channel created successfully! Channel info:")
            print(json.dumps(self.ChannelInfo ,indent=4))
            return TSwriteApiKey, ChannelID
        else:
            print("Channel creation failed! Please try again!")
            #sys.exit(0)
        
    
    def Update(self, TSwriteApiKey, measurement):
        TSupdateChannelInfo = {
                    "api_key": TSwriteApiKey,
                    "field1": measurement
                }
        TSupdate = requests.get(self.TSupdateURL + '.json', data = TSupdateChannelInfo).text
        #TSupdate = requests.get(TSupdateURL + '?api_key=' + TSwriteApiKey + '&field1={measurement}').text
        TSupdateInfo = json.loads(TSupdate)
        print(json.dumps(TSupdateInfo ,indent=4))
        
    def DeleteChannel(self, ChannelID):
        DeleteChannelURL = self.TSURL + '/' + str(ChannelID) + '.json'
        Deleted = requests.delete(DeleteChannelURL, data = self.API_keyDict).text
        print("Channel deleted successfully! Deleted channel info:")
        print(json.dumps(Deleted ,indent=4))
