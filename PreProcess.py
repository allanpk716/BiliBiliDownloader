# -*- coding: utf-8 -*-
import os
import operator as op
from VideoInfo import VideoInfo 
from UperInfo import UperInfo 

import asyncio

from Common import RandomSleep

from ruia_pyppeteer import PyppeteerRequest as Request
from Items import PageItem, BiliBiliItem, UserItem, VideoCountItem

class PreProcess():
    def __init__(self, **kwargs):
        super().__init__()
        # --------------------------------------------------------------------------------------
        # 日志
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        # --------------------------------------------------------------------------------------
        # 并凑出 UP 主的 Space Url
        if 'uperList' in kwargs:
            self.uperList = kwargs['uperList']
        else:
            info = "Error:You Need Set uperList"
            self.logger.error(info)
            raise Exception(info)
        # --------------------------------------------------------------------------------------
        self.logger.info("PreProcess Init Done.")

    # 扫描本地已经下载的信息
    def ScanLoclInfo(self, saveRootPath):
        for fpath, dirnames, fnames in os.walk(saveRootPath):
            # fpath    当前文件夹 root
            # dirnames  当前文件夹中包含的子文件夹名称列表，不包含路径
            # fnames    当前文件夹中的子文件列表，不包含路径
            folderName = ''
            if fpath:
                folderName = os.path.split(fpath)[1]
            nowUper = None
            for fname in fnames:
                if nowUper == None:
                    for uper in self.uperList:
                        if uper.UserName != folderName:
                            continue
                        else:
                            nowUper = uper
                if nowUper == None:
                    continue
                extensionName = os.path.splitext(fname)[-1]
                if op.eq(extensionName, '.flv') == True or op.eq(extensionName, '.mp4') == True:
                    vi = VideoInfo('')
                    # 将本地已经下载的文件，去除后缀名
                    vi.loaclFileName = fname.replace(extensionName, '')
                    vi.isDownloaded = True
                    nowUper.VideoInfoDic_loaclFileName[vi.loaclFileName] = vi

        self.logger.info('ScanLoclInfo Done.')
        self.logger.info("ScanLoclInfo Result"+ "----" * 20)
        for uper in self.uperList:
            self.logger.info('Local ' + uper.UserName + ' Got ' + str(len(uper.VideoInfoDic_loaclFileName)) + " Videos.")
        
    def ProcessOneUper(self, uper):
        self.logger.info('Analysis ' + uper.UserName + ' MainVideoPage Start···')
        pageInfo, videoCountInfo, userInfo = asyncio.get_event_loop().run_until_complete(self.GetPageInfo(uper.MainVideoPageUrl))
        uper.PageCount = pageInfo.count
        uper.NeedDownloadFilmCount = int(videoCountInfo.count)
        self.logger.info('Analysis ' + uper.UserName + ' MainVideoPage Done.')

    def Process(self):
        # 找到每个 UP 主有的页数
        for uper in self.uperList:
            # 必须找到总页数
            pgAllTime = 0
            while (uper.PageCount <= 0):
                if pgAllTime > 10:
                    raise Exception("Error:Try get " + uper.UserName + ' PageCount fail.')
                self.ProcessOneUper(uper)
                RandomSleep()
                pgAllTime = pgAllTime + 1

        self.logger.info('GetPageInfo Done.')
        # --------------------------------------------------------------------------------------
        # 把所有需要遍历的 page ，每一个 UP 主
        # 开启循环，把所有页遍历一次
        for uper in self.uperList:
            for index in range(1, uper.PageCount + 1):
                nowPageUrl = "https://space.bilibili.com/{0}/video?tid=0&page={1}&keyword=&order=pubdate".format(uper.UserId, index)
                uper.PageList.append(nowPageUrl)
        
        self.logger.info('PreProcess.Process Done.')

    async def GetPageInfo(self, url):
        self.logger.info("Requesting " + url)
        request = Request(url, load_js=True)
        response = await request.fetch()
        self.logger.info("fetched " + url)

        self.logger.info("PageItem.get_item start")
        pageInfo = await PageItem.get_item(html=response.html)
        self.logger.info("PageItem.get_item end")

        self.logger.info("VideoCountItem.get_item start")
        VideoCountInfo = await VideoCountItem.get_item(html=response.html)
        self.logger.info("VideoCountItem.get_item end")
    
        self.logger.info("UserItem.get_item start")
        userInfo = await UserItem.get_item(html=response.html)
        self.logger.info("UserItem.get_item end")

        return pageInfo, VideoCountInfo, userInfo
      