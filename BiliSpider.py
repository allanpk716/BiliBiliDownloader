# -*- coding: utf-8 -*-
import pretty_errors
import os
import operator as op
import re
import random
import time
import asyncio
from ruia_pyppeteer import PyppeteerSpider as Spider
from ruia_pyppeteer import PyppeteerRequest as Request

from Items import PageItem, BiliBiliItem, UserItem, VideoCountItem
from middlewares import middleware
from db import MotorBase

from LogHelper import LogHelper
from Downloader import Downloader
import GetUploadTimer
from Common import RandomSleep

class VideoInfo():
    def __init__(self, iurl):
        super().__init__()
        self.time = ''
        self.title = ''
        self.url = iurl
        # 包含后缀名
        self.loaclFileName = ''
        self.isDownloaded = False

class UperInfo():
    def __init__(self, iUserName, iUserId):
        super().__init__()
        self.UserName = iUserName
        self.UserId = iUserId
        # 目标下载多少个视频
        self.NeedDownloadFilmCount = 0
        # Uper 主 Video Url
        self.MainVideoPageUrl = 'https://space.bilibili.com/{0}/video'.format(self.UserId)
        # 有多少页
        self.PageCount = 0
        # 每一页的地址
        self.PageList = []
        # 每个视频的信息
        # 本地已经有的，可能会混有其他的不属于这个 Uper 的文件
        self.VideoInfoDic_loaclFileName = {}
        # 动态网上找到的
        self.VideoInfoDic_NetFileName = {}
        # 错误的 url
        self.ErrorUrl_Dic = {}
        self.ThisTimeDownloadCount = 0

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

def MainProcess(uperList, saveRootPath, concurrency = 3):
    logger = LogHelper('Bili', cmdLevel='INFO', fileLevel="DEBUG").logger
    pp = None
    try:
        # --------------------------------------------------------------
        # 进行每个 UP 主视频页数的获取
        pp = PreProcess(logger = logger, uperList=uperList)
        pp.ScanLoclInfo(saveRootPath)
        pp.Process()
        # --------------------------------------------------------------
        # 爬取要下载视频的 url
        for uper in pp.uperList:
            logger.info(uper.UserName + " Spider Start···")
            OneSpiderRetryTimes = 0
            # 打算下载的数量，要去网络动态获取的数量进行对比
            while ((uper.NeedDownloadFilmCount > len(uper.VideoInfoDic_NetFileName) or len(uper.ErrorUrl_Dic) > 0) and OneSpiderRetryTimes <= 10):
                BiliSpider.start(logger = logger,
                                uper = uper,
                                saveRootPath = saveRootPath,
                                concurrency = concurrency,
                                middleware=middleware)
                                
                OneSpiderRetryTimes = OneSpiderRetryTimes + 1
                logger.info("Try Spider " + uper.UserName + " " + str(OneSpiderRetryTimes) + " times.")
                RandomSleep()
                
            logger.info(uper.UserName + " Spider Done.")

            if OneSpiderRetryTimes > 10:
                logger.error(uper.UserName + " Spider Retry " + str(OneSpiderRetryTimes) + "times.")
                logger.error("Error Url:")
                for eUrl in uper.ErrorUrl_Dic:
                    logger.error(eUrl)
            else:
                # 本地应该原有+准备要下载的 != 网络总数，需要提示
                if len(uper.VideoInfoDic_NetFileName) != len(uper.VideoInfoDic_loaclFileName):
                    logger.warn("VideoInfoDic_NetFileName Count: " + str(len(uper.VideoInfoDic_NetFileName)) 
                        + " != VideoInfoDic_loaclFileName Count: " + str(len(uper.VideoInfoDic_loaclFileName))
                    )
            uper.ErrorUrl_Dic.clear()

        logger.info("Spider All Done.")
        # --------------------------------------------------------------
        logger.info("Start Download"+ "----" * 20)
        # 开始下载
        # 先对 local 与 net 的字典进行同步
        logger.info("Start Sync Dic")
        for uper in pp.uperList:
            iNeedDl = 0
            for fileName, oneVideo in zip(uper.VideoInfoDic_loaclFileName.keys(), uper.VideoInfoDic_loaclFileName.values()):
                if fileName in uper.VideoInfoDic_NetFileName:
                    uper.VideoInfoDic_NetFileName[fileName].isDownloaded = oneVideo.isDownloaded
                    if oneVideo.isDownloaded == False:
                        iNeedDl = iNeedDl + 1
            logger.info(uper.UserName + "NetFile / LocalFile -- NeedDl: " + str(len(uper.VideoInfoDic_NetFileName)) + " / " + str(len(uper.VideoInfoDic_loaclFileName)) + " -- " + str(iNeedDl))
        logger.info("End Sync Dic")
        for uper in pp.uperList:
            directory = os.path.join(saveRootPath, uper.UserName)
            for fileName, oneVideo in zip(uper.VideoInfoDic_NetFileName.keys(), uper.VideoInfoDic_NetFileName.values()):
                if oneVideo.isDownloaded == True:
                    continue
                DownloadRetryTimes = 0
                oneRe = False
                while oneRe is False and DownloadRetryTimes <= 10:
                    oneRe = Downloader(logger, directory, oneVideo.time, oneVideo.title, oneVideo.url).ProcessOne()
                    DownloadRetryTimes = DownloadRetryTimes + 1
                    logger.info("Try Download " + str(DownloadRetryTimes) + " times.")
                    RandomSleep()

                if OneSpiderRetryTimes > 10:
                    logger.error("Retry Download " + str(DownloadRetryTimes) + " times.")
                    logger.error("Error Url: " + oneVideo.url)
                # 标记下载完成
                if oneRe:
                    oneVideo.isDownloaded = True
                    uper.ThisTimeDownloadCount = uper.ThisTimeDownloadCount + 1
                    

    except Exception as ex:
        errInfo = "Catch Exception: " + str(ex)
        logger.error(errInfo)
    finally:
        logger.info("finally"+ "----" * 20)
        for uper in pp.uperList:
            logger.info("This Time Download: " + uper.UserName + " -- " + str(uper.ThisTimeDownloadCount))
        for uper in pp.uperList:
            for fileName, oneVideo in zip(uper.VideoInfoDic_NetFileName.keys(), uper.VideoInfoDic_NetFileName.values()):
                if oneVideo.isDownloaded == False:
                    logger.error('Download Fail:' + uper.UserName)
                    logger.error(oneVideo.url)
        logger.info("All Done.")

if __name__ == '__main__':
    # --------------------------------------------------------------
    # 设置需要下载的信息
    # 每个 UP 主视频的总数
    uperList = []
    # https://space.bilibili.com/9458053/video
    #                        用户名        用户的 VideoPage ID数
    uperList.append(UperInfo('李永乐',          '9458053'))
    uperList.append(UperInfo('巫师财经',        '472747194'))
    # uperList.append(UperInfo('回形针PaperClip', '258150656'))
    # uperList.append(UperInfo('柴知道',          '26798384',))
    saveRootPath = r'D:\Bilibili'
    # 并发数
    concurrency = 3

    MainProcess(uperList, saveRootPath, concurrency)
    