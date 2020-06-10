import requests
import datetime
from bs4 import BeautifulSoup
import fakeagent

def Get(inUrl):
    inUrl = 'https://' + inUrl
    headers = {'User-Agent': fakeagent.ua.random}
    requestSession = requests.session()
    result = requestSession.get(inUrl, headers=headers)
    if result.status_code == 200:
        soup = BeautifulSoup(result.text, 'lxml')
        items = soup.find_all(name='div',attrs={"class":"video-data"})
        if len(items) != 2:
            raise Exception("div - class - video-data not 2 Items")
        dtRoot = items[0]
        dtRoot = dtRoot.find_all(name='span')
        if len(dtRoot) != 2:
            raise Exception("span not 2 Items")
        strTime = dtRoot[1].text
        date = datetime.datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S')
        nowTime = date.strftime("%Y-%m-%d")
        return nowTime
    else:
        return None
    