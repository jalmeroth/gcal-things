#!/usr/bin/env python
import logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()
logger = logging.getLogger(__name__)

import json
import time
import urllib
import webapp2

from datetime import datetime, date, timedelta
from oauth2.auth import Authenticator
from helpers import load, GMT1
from things import ccThings

class DailyRequest(webapp2.RequestHandler):
    """docstring for DailyRequest"""
    def __init__(self, request, response):
        """docstring for __init__"""
        # Set self.request, self.response and self.app.
        self.initialize(request, response)
        json_file = "credentials.json"
        self.prefs = load(json_file)
        
        client_id = self.prefs.get('client_id')
        client_secret = self.prefs.get('client_secret')
        scope = ['https://www.googleapis.com/auth/calendar.readonly']
        tokens = self.prefs.get('tokens')
        
        self.auth = Authenticator(client_id, client_secret, scope, tokens)
    
    def preProcess(self, events, mini, setDueDate = False):
        """docstring for preProcess"""
        items = {}
        
        for event in events:
            allday = event['end'].get('date')   #2014-08-30
            
            if allday and allday == mini: # ignore previous day events
                # print "Passing", event.get('summary', "No summary"), mini, allday
                pass
            else:
                ident = event.get('id')
                title = "Termin:" + " " + event.get('summary', "No summary")
                note = event.get('description', None)
                duedate = event['start'].get('date', None) if setDueDate else None
                
                items[ident] = {
                    "title": title,
                    "note": note,
                    "duedate": duedate
                }
        
        return items
    
    def fetch(self, user_id, calendarId = "primary", timeMin = None, timeMax = None):
        """docstring for fetch
        
        Events: list
        https://developers.google.com/google-apps/calendar/v3/reference/events/list
        
        """
        today = date.today()
        tomorrow = today + timedelta(days=+1)
        
        mini = timeMin if timeMin else today.isoformat()
        maxi = timeMax if timeMax else tomorrow.isoformat()
        
        # print today, tomorrow
        timeMin = self._rfc3339(mini)
        timeMax = self._rfc3339(maxi)
        
        url = "https://www.googleapis.com/calendar/v3/calendars/" + urllib.quote(calendarId) + "/events"
        
        items = []
        pageToken = ""
        
        while True:
            
            params = {
                "orderBy": "startTime",
                "singleEvents": True,
                "timeMax": timeMax,
                "timeMin": timeMin,
                "pageToken": pageToken,
                "fields": "items(id,description,summary,start,end),nextPageToken"
            }
            
            logger.info("Fetching events between {0} and {1} from {2}#{3}".format(str(timeMin), str(timeMax), user_id, calendarId))
            
            r = self.auth.signedRequest(url, user_id, params=params)
            
            if r.ok:
                data = r.json()
                items += data.get('items', [])
                pageToken = data.get('nextPageToken')
            else:
                logger.info("There was an error while fetching your data.")
            
            if not pageToken:
                break
        
        logger.info("Found " + str(len(items)) + " items")
        return items
    
    def _rfc3339(self, datum, sep = "T"):
        """docstring for _rfc3339"""
        dtnaive = datetime.strptime(datum, "%Y-%m-%d")
        dt_gmt1 = dtnaive.replace(tzinfo=GMT1())
        return dt_gmt1.isoformat(sep)
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        
        param_config = self.request.params.get('config', 'default')
        configs = self.prefs.get('configs', {})
        config = configs.get(param_config)
        
        if config:
            
            users = config.get('users', [])
            accountId = config.get('ccAccountId')
            
            tokens = self.prefs.get('tokens')
            items = {}
            
            today = date.today()
            tomorrow = today + timedelta(days=+1)
            logger.info("today: " + str(today) + " tomorrow: " + str(tomorrow))
            
            for user_id in users:
                
                mini = today.isoformat()
                maxi = tomorrow.isoformat()
                logger.info("mini: " + str(mini) + " maxi: " + str(maxi))
                
                events = self.fetch(user_id, 'primary', mini, maxi)
                items.update(self.preProcess(events, mini))
                self.response.write(json.dumps(events) + "\n")
                
                events = self.fetch(user_id, '#contacts@group.v.calendar.google.com', mini, maxi)
                items.update(self.preProcess(events, mini, True))
                self.response.write(json.dumps(events) + "\n")
                
                mini = (today + timedelta(days=+2)).isoformat()
                maxi = (today + timedelta(days=+3)).isoformat()
                
                events = self.fetch(user_id, '#contacts@group.v.calendar.google.com', mini, maxi)
                items.update(self.preProcess(events, mini, True))
                self.response.write(json.dumps(events) + "\n")
            
            # print(items)
            
            if len(items) and accountId:
                logger.info("Building new taskset")
                things = ccThings(accountId)
                data = things.newTaskSet(items)
                self.response.write(json.dumps(data) + "\n")
                
                logger.info("Posting data to Things Cloud...")
                result = things.submitTaskSet(data)
                result = json.loads(result)
                if result['current-item-index']:
                    logger.info("Success.")
            else:
                logger.debug("No new items found.")
            
            self.response.write(json.dumps(items) + "\n")

app = webapp2.WSGIApplication([
        ('/daily', DailyRequest)
], debug=True)
