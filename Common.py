# -*- coding: utf-8 -*-
import random
import time
import requests
import asyncio
from ruia_pyppeteer import PyppeteerRequest as Request
from fake_useragent import UserAgent
ua = UserAgent()

def RandomSleep():
    time.sleep(random.randint(0, 5))

def CheckRedirectUrl(url):
    inUrl = 'https://' + url
    headers = {'User-Agent': ua.random}
    requestSession = requests.session()
    result = requestSession.get(inUrl, headers=headers)
    if result.status_code == 200:
        if result.history:
            if result.history[0].status_code == 302:
                GetRedirectUrl(result.url)
        return result.url
    elif result.status_code == 302:
        pass
    else:
        return None

async def GetOneUrl(url):
        # url = 'https://' + url
        request = Request(url, load_js=True, dumpio=True)
        response = await request.fetch()
        return response.url

def GetRedirectUrl(url):
    asyncio.get_event_loop().run_until_complete(GetOneUrl(url))
