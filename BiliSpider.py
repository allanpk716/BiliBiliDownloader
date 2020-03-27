# -*- coding: utf-8 -*-
import re
import random
import asyncio
from VideoInfo import VideoInfo 
import GetUploadTimer

from Items import BiliBiliItem
from ruia_pyppeteer import PyppeteerSpider as Spider
# from ruia import *

  
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
        # UPer List
        if 'uper' in kwargs:
            self.uper = kwargs['uper']
        else:
            info = "Error:You Need Set uper"
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
        # 并发数
        if 'concurrency' in kwargs:
            self.concurrency = kwargs['concurrency']
        else:
            self.concurrency = 1
        # --------------------------------------------------------------------------------------
        # 拼接 start_urls，也就是 PageList
        # 如果 错误的 url 有，那么start_urls 就要替换
        self.start_urls.clear()
        if len(self.uper.ErrorUrl_Dic) == 0:
            for onePageUrl in self.uper.PageList:
                self.start_urls.append(onePageUrl)
        else:
            self.start_urls.clear()
            for onePageUrl in self.uper.ErrorUrl_Dic:
                self.start_urls.append(onePageUrl)
            # 需要清空
            self.uper.ErrorUrl_Dic.clear()
        
        self.lock = asyncio.Lock()
        self.logger.info("start_urls Count: " + str(len(self.start_urls)))

    async def parse(self, response):
        if response is None:
            return
        self.logger.info(response.url)
        self.logger.info("for BiliBiliItem.get_items ···")
        try:
            async for item in BiliBiliItem.get_items(html=response.html):
                self.logger.info("parsing one···")
                if item.time is None:
                    item.time = GetUploadTimer.Get(item.url)
                self.logger.info(item.time)
                self.logger.info(item.title)
                self.logger.info(item.url)
                # 去除特殊字符，不包含后缀名
                fileName = re.sub('[\/:*?"<>|]','-', item.title)
                fileName = item.time + "_" + fileName
                # 是否已经在本地扫描的时候找到了相同的文件名
                vi = VideoInfo(item.url)
                vi.time = item.time
                vi.title = item.title
                vi.isDownloaded = False
                vi.loaclFileName = fileName

                try:
                    await self.lock.acquire()
                    if fileName in self.uper.VideoInfoDic_loaclFileName:
                        # 存在，则赋值 url 等信息
                        self.uper.VideoInfoDic_loaclFileName[fileName].url = item.url
                        self.uper.VideoInfoDic_loaclFileName[fileName].time = item.time
                        self.uper.VideoInfoDic_loaclFileName[fileName].title = item.title
                    else:
                        # 不存在，新建
                        self.uper.VideoInfoDic_loaclFileName[fileName] = vi
                    # 网络动态获取到的
                    self.uper.VideoInfoDic_NetFileName[fileName] = vi
                finally:
                    self.lock.release()
                
        except Exception as ex:
            try:
                await self.lock.acquire()
                self.uper.ErrorUrl_Dic[response.url] = str(ex)
                self.logger.error("Error BiliBiliItem: " + ex)
            finally:
                self.lock.release()
            

        self.logger.info("parsing one Done·")


    