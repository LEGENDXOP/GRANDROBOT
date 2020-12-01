import urllib.request as url
import json
import datetime
import requests

VERSION = "1.3.3"
CAS_QUERY_URL = "https://api.cas.chat/check?user_id="
DL_DIR = "./csvExports"

def get_user_data(user_id):
    with requests.request('GET', CAS_QUERY_URL + str(user_id)) as userdata_raw:
        userdata = json.loads(userdata_raw.text)
        return userdata

def isbanned(userdata):
    return userdata['ok']

def banchecker(user_id):
    return isbanned(get_user_data(user_id))

def vercheck() -> str:
    return str(VERSION)

def offenses(user_id):
    userdata = get_user_data(user_id)
    try:
        offenses = userdata['result']['offenses']
        return str(offenses) 
    except:
        return None
    
def timeadded(user_id):
    userdata = get_user_data(user_id)
    try:
        timeEp = userdata['result']['time_added']
        timeHuman = datetime.datetime.utcfromtimestamp(timeEp).strftime('%H:%M:%S, %d-%m-%Y')
        return timeHuman
    except:
        return None
