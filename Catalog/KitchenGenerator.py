# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 21:24:57 2022

@author: Alex Xie
"""
import json

class KitchenGenerator():
    def __init__(self):
        pass
    def Generator(self, ID):
        kitchenNum = int(ID)//100
        kitchen = {
            "kitchenNumber": f"{kitchenNum}",
            "TempTopic": f"kitchen/sensor/temperature/{kitchenNum}",
            "MotionTopic": f"kitchen/sensor/motion/{kitchenNum}",
            "ValveTopic": f"kitchen/valve/{kitchenNum}",
            "noderedTopic": f"nodered/kitchen/valve/{kitchenNum}"
            }
        
        return kitchen
