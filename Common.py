# -*- coding: utf-8 -*-
import random
import time
import re
import requests
from ABV import ABV
from fake_useragent import UserAgent
ua = UserAgent()

def RandomSleep():
    time.sleep(random.randint(0, 5))

def CheckRedirectUrl(url):
    inUrl = 'https://' + url
    headers = {'User-Agent': ua.random}
    requestSession = requests.session()

    fAv = r'/av(\d+)/*'
    fBv = r'/BV(.*$)'

    AVID = ''
    reSearch = re.search(fAv, inUrl)
    if reSearch is None:
        reSearch = re.search(fBv, inUrl)
        if reSearch is None:
            return None
        abv = ABV()
        AVID = abv.dec(reSearch.group(0).replace('/', ''))
        AVID = str(AVID)
    else:
        AVID = reSearch.group(1)
            
    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + AVID
    
    result = requestSession.get(start_url, headers=headers)
    if result.status_code == 200:
        if 'redirect_url' in result.json()['data']:
            return result.json()['data']['redirect_url']
        else:
            return url
    else:
        return None
