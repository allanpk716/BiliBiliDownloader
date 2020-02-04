# -*- coding: utf-8 -*-
import re
import asyncio
from ruia_pyppeteer import PyppeteerSpider as Spider
from ruia_pyppeteer import PyppeteerRequest as Request

from Items import PageItem, BiliBiliItem, UserItem
from middlewares import middleware
from db import MotorBase

import os
import sys
from you_get import common as you_get

from LogHelper import LogHelper

g_downloadItemCount_dic = {}

class PreProcess():
    def __init__(self, **kwargs):
        super().__init__()
        # --------------------------------------------------------------------------------------
        # 日志
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        # --------------------------------------------------------------------------------------
        # 便于后续从 Url 得到 PageCount
        self.start_urls_PageCount_dic = {}
        # 便于后续从 Url 得到 UserID
        self.start_urls_UserID_dic = {}
        # 用户名字典
        self.start_urls_UserInfo_dic = {}
        # --------------------------------------------------------------------------------------
        # 并凑出 UP 主的 Space Url
        if 'start_urls' in kwargs:
            # 预处理缓存
            self.start_urls_Pre = []
            for oneI in kwargs['start_urls']:
                tmpUrl = 'https://space.bilibili.com/{0}/video'.format(oneI)
                self.start_urls_Pre.append(tmpUrl)
                self.start_urls_UserID_dic[tmpUrl] = oneI
        else:
            info = "Error:You Need Set start_urls"
            self.logger.error(info)
            raise Exception(info)
        # --------------------------------------------------------------------------------------
        # 找到每个 UP 主有的页数
        for oneSpaceUrl in self.start_urls_Pre:
            pageInfo, userInfo = asyncio.get_event_loop().run_until_complete(self.GetPageInfo(oneSpaceUrl))
            self.start_urls_PageCount_dic[oneSpaceUrl] = pageInfo.count
            self.start_urls_UserInfo_dic[oneSpaceUrl] = userInfo.UserName
        self.logger.info('GetPageInfo Done.')
        # --------------------------------------------------------------------------------------
        # 把所有需要遍历的 page ，每一个 UP 主的，都拼接到 self.start_urls
        self.start_urls = []
        self.start_urls_UserName_dic = {}
        for oneSpaceUrl in self.start_urls_Pre:
            # 有多少页
            nowpgCount = self.start_urls_PageCount_dic[oneSpaceUrl]
            # 获取当前的 UserID
            nowUserID = self.start_urls_UserID_dic[oneSpaceUrl]
            # 当前的 UP 主的名字
            nowUserName = self.start_urls_UserInfo_dic[oneSpaceUrl]
            # 开启循环，把所有页遍历一次
            for index in range(1, nowpgCount + 1):
                nowPageUrl = "https://space.bilibili.com/{0}/video?tid=0&page={1}&keyword=&order=pubdate".format(nowUserID, index)
                self.start_urls.append(nowPageUrl)
                self.start_urls_UserName_dic[nowPageUrl] = nowUserName
                # to-do 只加一条！
                # break

    async def GetPageInfo(self, url):
        self.logger.info("Requesting " + url)
        request = Request(url, load_js=True)
        response = await request.fetch()
        self.logger.info("fetched " + url)

        self.logger.info("PageItem.get_item start")
        pageInfo = await PageItem.get_item(html=response.html)
        self.logger.info("PageItem.get_item end")

        self.logger.info("UserItem.get_item start")
        userInfo = await UserItem.get_item(html=response.html)
        self.logger.info("UserItem.get_item end")

        return pageInfo, userInfo
        
class BiliSpider(Spider):
    start_urls = ['']
    concurrency = 1

    def __init__(self, middleware=None, loop=None, is_async_start=False, cancel_tasks=True, **kwargs):
        super().__init__(middleware=middleware, loop=loop, is_async_start=is_async_start, cancel_tasks=cancel_tasks, **kwargs)
        # --------------------------------------------------------------------------------------
        # 日志
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        # --------------------------------------------------------------------------------------
        # 并凑出 UP 主的 Space Url
        if 'start_urls' in kwargs:
            # 预处理缓存
            self.start_urls = kwargs['start_urls']
        else:
            info = "Error:You Need Set start_urls"
            self.logger.error(info)
            raise Exception(info)
        # --------------------------------------------------------------------------------------
        # 当前下载地址对应的 rootPath
        if 'saveRootPath' in kwargs:
            # 预处理缓存
            self.saveRootPath = kwargs['saveRootPath']
        else:
            info = "Error:You Need Set saveRootPath"
            self.logger.error(info)
            raise Exception(info)
        # --------------------------------------------------------------------------------------
        # 当前下载地址对应的
        if 'start_urls_UserName_dic' in kwargs:
            # 预处理缓存
            self.start_urls_UserName_dic = kwargs['start_urls_UserName_dic']
        else:
            info = "Error:You Need Set start_urls_UserName_dic"
            self.logger.error(info)
            raise Exception(info)
        # --------------------------------------------------------------------------------------
        # 并发数
        if 'concurrency' in kwargs:
            self.concurrency = kwargs['concurrency']
        else:
            self.concurrency = 1

        # 存储每个 Up 主下载了多少集
        global g_downloadItemCount_dic
        for oneUrl in self.start_urls:
            g_downloadItemCount_dic[self.start_urls_UserName_dic[oneUrl]] = 0
        
        self.logger.info("start_urls Count: " + str(len(self.start_urls)))

    async def parse(self, response):
        self.logger.info("for BiliBiliItem.get_items ···")
        self.logger.info(response.url)
        async for item in BiliBiliItem.get_items(html=response.html):
            self.logger.info("parsing···")
            self.logger.info(item.title)
            self.logger.info(item.url)
            nowUserName = self.start_urls_UserName_dic[response.url]
            directory = os.path.join(self.saveRootPath, nowUserName)
            # 去除特殊字符，否则下载文件会有问题
            fileName = re.sub('[\/:*?"<>|]','-', item.title)
            sys.argv = ['you-get','--debug', '-o', directory, '-O', item.time + "_" + fileName, item.url]
            self.logger.info("start download···")
            you_get.main()
            self.logger.info("end download")
            global g_downloadItemCount_dic
            g_downloadItemCount_dic[nowUserName] = g_downloadItemCount_dic[nowUserName] + 1

    # async def process_item(self, item):
    #     await print(item.title)

if __name__ == '__main__':
    logger = LogHelper('Bili', debug=True, cmdLevel='INFO', fileLevel="DEBUG").logger
    try:
        # 李永乐
        # start_urls = ['https://space.bilibili.com/9458053/video']
        # 巫师财经
        # start_urls = ['https://space.bilibili.com/472747194/video']
        # 回形针PaperClip
        # start_urls = ['https://space.bilibili.com/258150656/video']
        # 柴知道
        # start_urls = ['https://space.bilibili.com/26798384/video']
        start_urls = [
            '9458053',      # 李永乐
            '472747194',    # 巫师财经
            '258150656',    # 回形针PaperClip
            '26798384',     # 柴知道
        ]
        concurrency = 1
        saveRootPath = r'D:\Bilibili'

        pp = PreProcess(start_urls=start_urls, logger = logger)

        assert len(pp.start_urls) > 0, 'Error: Check your network. pp.start_urls <= 0 '
        
        BiliSpider.start(logger = logger,
                        start_urls=pp.start_urls,
                        saveRootPath = saveRootPath,
                        start_urls_UserName_dic = pp.start_urls_UserName_dic,
                        concurrency=concurrency, 
                        middleware=middleware)
    except Exception as ex:
        logger.error(ex)
    finally:
        # global g_downloadItemCount_dic
        for k, v in zip(g_downloadItemCount_dic.keys(), g_downloadItemCount_dic.values()):
            print(k + " -- " + str(v))
        logger.info("All Done.")
    