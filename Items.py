# -*- coding: utf-8 -*-
import re
import datetime
from ruia import AttrField, TextField, Item

class BiliBiliItem(Item):
    target_item = TextField(css_select='li.small-item.fakeDanmu-item')
    title = TextField(css_select='a.title')
    url = AttrField(css_select='a.title', attr='href')
    time = TextField(css_select='span.time')

    async def clean_url(self, value):
        index = value.find(r'//')
        if index < 0:
            return value
        elif index == 0:
            newValue = value.replace(r'//', '')
            return newValue

    async def clean_time(self, value):
        # 说明日期不符合格式，估计是中文，比如，昨天
        if value.find('-') < 0:
            return None
            
        vlist = value.split('-')
        # Y M D
        if len(vlist) == 3:
            date = datetime.datetime.strptime(value, '%Y-%m-%d')
            nowTime = date.strftime("%Y-%m-%d")
            return nowTime
        elif len(vlist) == 2:
            date = str(datetime.datetime.now().year) + "-" + value
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            nowTime = date.strftime("%Y-%m-%d")
            return nowTime
        else:
            raise Exception("Error:BiliBiliItem clean_time else " + nowTime)

class UserItem(Item):
    target_item = TextField(css_select='div.h-user')
    UserName = TextField(xpath_select='//span[@id="h-name"]')

class PageItem(Item):
    target_item = TextField(css_select='div.content')
    count = TextField(css_select='span.be-pager-total')

    async def clean_count(self, value):
        nowpgCount = 1
        pgc = re.findall(r"\d+\.?\d*", value)
        if pgc:
            nowpgCount = int(pgc[0])
        else:
            raise Exception("Error:PageItem re.findall -> pageInfo.count")
        return nowpgCount

class VideoCountItem(Item):
    target_item = TextField(css_select='li.contribution-item.cur')
    count = TextField(css_select='span.num')