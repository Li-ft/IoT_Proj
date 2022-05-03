# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 19:14:21 2022

@author: Alex Xie
"""

import json
import time
import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from MyMQTT import *


class SwitchBot:
    exposed=True
    def __init__(self):
        self.serviceInfo = json.load(open('TelegramService.json'))
        self.catelogAddress = self.serviceInfo["CatelogAddress"]
        self.serviceID = self.serviceInfo["serviceID"]
        brokerInformation = requests.get(self.serviceInfo["brokerInquiry"]).json()
        brokerInfo = brokerInformation["Brokers in the catalog"]
        broker = brokerInfo["broker"]
        port = int(brokerInfo["port"])
        clientID = self.serviceInfo["serviceName"]
        self.telegramToken = ""
        self.chatIDs=[]
        self.client = MyMQTT(clientID, broker, port, self)
        self.valveTopic = ""
        self.dangervalveTopic = ""
        self.__message={
            "bn": "",
            "bnn": "",
            "e": [{
                "n": "switch",
                "v": ""
                    }]
            }
        #MessageLoop(self.bot, {'chat': self.on_chat_message,
                               #'callback_query': self.on_callback_query}).run_as_thread()
    def start(self):
        self.client.start()
        conf = requests.post(self.catelogAddress, json=self.serviceInfo).text
        config = json.loads(conf)
        self.valveTopic = config["valveTopic"]
        self.telegramToken = config["telegramToken"]
        self.bot = telepot.Bot(self.telegramToken)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()
        self.client.mySubscribe(self.valveTopic)

    def stop(self):
        self.client.stop()
        requests.delete(self.catelogAddress + "/service/" + self.serviceID)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.chatIDs.append(chat_ID)
        message = msg['text']
        
        if message=="/start_bot":
            self.bot.sendMessage(chat_ID, text='The smart valve is started.')
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported.")
        
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        payload = self.__message.copy()
        payload["bn"] = self.dangervalveTopic
        payload["bnn"] = self.dangervalveTopic
        payload['e'][0]['v'] = int(query_data)
        valveNum = payload["bn"][-1]
        if query_data == "0":
            self.bot.sendMessage(chat_ID, text=f"Turning OFF the Valve #{valveNum}...")
        elif query_data == "1":
            self.bot.sendMessage(chat_ID, text=f"Turning ON the Valve #{valveNum}...")
        else:
            pass
        self.client.myPublish(self.dangervalveTopic, json.dumps(payload))
        
    def notify(self,topic,message):
        payload=json.loads(message)
        if payload["e"][0]["n"] == "temperature":
            self.dangervalveTopic = payload["bn"]
            valveNum = payload["bn"][-1]#"kitchen/valve/1"
            dangerMsg = f"ATTENTION!!!\nValve #{valveNum} is overheated!"
            for chat_ID in self.chatIDs:
                #buttons = [[InlineKeyboardButton(text='TURN OFF', callback_data='0')]]
                #keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                #self.bot.sendMessage(chat_ID, text=dangerMsg, reply_markup=keyboard)
                self.bot.sendMessage(chat_ID, text=dangerMsg)
        elif payload["e"][0]["n"] == "switch" or "teleswitch":
            self.dangervalveTopic = payload["bnn"]
            valveNum = payload["bnn"][-1]#"kitchen/valve/1"
            valveStatus = bool(payload["e"][0]["v"])
            if valveStatus:
                turnOn = f"Valve #{valveNum} is turned on."
                for chat_ID in self.chatIDs:
                    buttons = [[InlineKeyboardButton(text='TURN OFF', callback_data='0')]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text=turnOn, reply_markup=keyboard)
            else:
                turnOff = f"Valve #{valveNum} is turned off."
                for chat_ID in self.chatIDs:
                    buttons = [[InlineKeyboardButton(text='TURN ON', callback_data='1')]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text=turnOff, reply_markup=keyboard)


if __name__ == "__main__":
    SwitchBot = SwitchBot()
    SwitchBot.start()
    print("Switch Bot is running...")
    print("Enter 'q' to exit")
    while (True):
        if input() == 'q':
            break
        else:
            pass
    SwitchBot.stop()
