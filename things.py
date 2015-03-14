#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import calendar
import datetime
import time
import uuid
import json
import urllib
import logging
logger = logging.getLogger(__name__)

from oauth2.request import WebRequest


class ccThings(object):
    """docstring for ccThings"""
    def __init__(self, accountId):
        super(ccThings, self).__init__()
        self.accountId = accountId
    
    def timeFromIsoDate(self, date):
        """docstring for timeFromIsoDate"""
        return int(calendar.timegm(time.strptime(date, "%Y-%m-%d")))
    
    def newTaskSet(self, data):
        """docstring for newTaskSet"""
        taskSet = [{}]
        
        for key, item in data.items():
            
            uid = str(uuid.uuid4()).upper()
            now = time.time()
            day = self.timeFromIsoDate(datetime.date.today().isoformat())
            
            title = item.get('title', 'New To Do')
            duedate = item.get('duedate', None)
            note = item.get('note', None)
            where = item.get('where', 'TODAY')
            
            if duedate:
                duedate = self.timeFromIsoDate(duedate)
                
            if note:
                note = '<note xml:space=\"preserve\">' + note + '</note>'
            
            st = 2 if where == "TODAY" else 0   # inbox: 0, today: 2
            sr = day if st > 0 else None        # if today, start date
            
            item = { uid: {
                    "e": "Task2",
                    "p": {
                        "acrd": None,
                        "ar": [],
                        "cd": now,
                        "dd": duedate,
                        "dl": [],
                        "do": 0,
                        "icc": 0,
                        "icp": False,
                        "icsd": None,
                        "ix": 0,
                        "md": now,
                        "nt": note,
                        "pr": [],
                        "rr": None,
                        "rt": [],
                        "sp": None,
                        "sr": sr,
                        "ss": 0, 
                        "st": st, 
                        "tg": [], 
                        "ti": 0, 
                        "tp": 0, 
                        "tr": False, 
                        "tt": title
                    },
                    "t": 0
                }
            }
            taskSet[0].update(item)
    
        accountId = getattr(self, "accountId", False)
        data = {}
        
        if accountId:
            
            currIndex = self.getCurrentIndex(accountId)
            
            data = {
                "current-item-index": currIndex,
                "items": taskSet,
                "schema": 1
            }
            
        return data

    def getCurrentIndex(self, accountId, currIndex = 10101):
        """docstring for getCurrentIndex
        * Find the current-item-index
        *
        * @param {string} accountId users account id
        * @param {number} index last known item count
        * @return {number} index current item count
        """
        
        accountId = str(accountId)
        currIndex = str(currIndex)
        
        if accountId:
            # print "Using:", accountId, currIndex
            
            url_history = "https://thingscloud.appspot.com/version/1/history/"
            url_history += urllib.quote(accountId)
            url_history += "/items?start-index=" + currIndex
            # print url_history
            
            headers = {
                "Content-Type" : "application/json"
            }
            
            data = self.makeRequest(url_history, headers=headers)
            data = json.loads(data)
            
            return data.get('current-item-index')
    
    def submitTaskSet(self, data):
        """docstring for submitTaskSet"""
        accountId = getattr(self, "accountId", False)
        
        if accountId:
            url = "https://thingscloud.appspot.com/version/1/history/" + accountId + "/items";
            
            headers = {
                "User-Agent": "ThingsMac/20201011fs (x86_64; OS X 10.8.3; en_DE; trial)",
                "Accept": "*/*",
                "Accept-Language": "en-us",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Content-Encoding": "UTF-8"
            }
            
            return self.makeRequest(url, method='POST', headers=headers, data=json.dumps(data))
    
    def makeRequest(self, url, **kwargs):
        # print headers
        r = WebRequest()
        result = r.req(url, **kwargs)
        return result.text
