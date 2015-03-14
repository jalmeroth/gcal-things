#!/usr/bin/python
import logging
logger = logging.getLogger(__name__)
import os
import json
import time
import calendar
import datetime


def timeFromIsoDate(date):
    """docstring for timeFromIsoDate"""
    return int(calendar.timegm(time.strptime(date, "%Y-%m-%d")))

def dateFromTime(time):
    """docstring for dateFromTime"""
    return datetime.datetime.fromtimestamp(
                float(time)
                ).strftime('%Y-%m-%d %H:%M:%S')

def dateFromIsoDate(date, sep=" "):
    """docstring for dateFromIsoDate"""
    return datetime.datetime.fromtimestamp(
                time.mktime(time.strptime(date, "%Y-%m-%d"))
                ).strftime('%Y-%m-%d'+ sep +'%H:%M:%S')

def work_dir(path = './store/'):
    """docstring for _work_dir"""
    file_dir = os.path.dirname(__file__)
    joint = os.path.join(file_dir, path)
    real_dir = os.path.realpath(joint)
    return real_dir

def save(data, filename):
    """docstring for save"""
    file = os.path.join(work_dir(), filename)
    with open(file, "w+") as jsonFile:
        json.dump(data, jsonFile)
    
def load(filename):
    """docstring for load"""
    file = os.path.join(work_dir(), filename)
    
    if os.path.exists(file):
        with open(file,"r") as jsonFile:
            return json.load(jsonFile)
    else:
        return {}

def main():
    """docstring for main"""
    now = time.time()

    day = datetime.date.today()
    today = day.isoformat()
    
    if time.daylight:
        print dateFromIsoDate(today, "T")+"+02:00" # GMT+1+Daylight
    else:
        print dateFromIsoDate(today, "T")+"+01:00" #GMT+1
        
    print timeFromIsoDate(today)
    print dateFromTime(now)
    print dateFromIsoDate(today)

if __name__ == '__main__':
    main()