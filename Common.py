# -*- coding: utf-8 -*-
import random
import time
import re
import requests
from fake_useragent import UserAgent
ua = UserAgent()

def RandomSleep():
    time.sleep(random.randint(0, 5))

def CheckRedirectUrl(url):
    inUrl = 'https://' + url
    headers = {'User-Agent': ua.random}
    requestSession = requests.session()

    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + re.search(r'/av(\d+)/*', inUrl).group(1)
    
    result = requestSession.get(start_url, headers=headers)
    if result.status_code == 200:
        return result.json()['data']['redirect_url']
    else:
        return None
