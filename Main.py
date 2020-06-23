# -*- coding: utf-8 -*-
import pretty_errors
import os
import re
import time
import requests
import configparser
from LogHelper import LogHelper
from UperInfo import UperInfo 
from PreProcess import PreProcess 
from Downloader import Downloader
from Common import RandomSleep
from middlewares import middleware

from BiliSpider import BiliSpider

repattern = r"\d{4}-\d{2}-\d{2}_"

class ConfigInfo():
    def __init__(self):
        self.saveRootPath = ""
        self.concurrency = ""
        self.barkurl = ""
        self.barkapikey = ""
        self.notifyurl = ""
        self.repeatTimes = 1
        self.delay = 0

# 结束 chrome 的僵尸进程
def CloseChrome():
    import platform
    sysstr = platform.system()
    if(sysstr =="Windows"):
        print("Call Windows tasks")
        os.system('taskkill /im chrome.exe /F')
    elif(sysstr == "Linux"):
        print("Call Linux tasks")
        os.system('pkill chrome')
    else:
        print("Other System tasks")

def ReadDownloadList(downloadfile):
    uperList = []
    f = open(downloadfile, "r", encoding="utf-8")
    lines = f.readlines()
    for line in lines:
        items = line.split('#')
        if len(items) != 2:
            raise Exception("DownloadList.txt Error," + line)
        oneUper = UperInfo(items[0].strip(), int(items[1].strip()))
        uperList.append(oneUper)
    f.close()
    return uperList

def MainProcess(logger, uperList, saveRootPath, concurrency = 3):
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
                # dd = BiliSpider()
                # GithubDeveloperSpider
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
                # 匹配到对应的项目才进行处理
                findList = list(filter(lambda d: d.split('_')[1] == fileName, uper.VideoInfoDic_NetFileName.keys()))
                if any(findList):
                    uper.VideoInfoDic_NetFileName[findList[0]].isDownloaded = oneVideo.isDownloaded
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
        logger.info("This Time Done.")

def BarkMe(barkurl, apikey, title, url4show):
    try:
        url = barkurl + '/' + apikey + '/' + title + '?url=' + url4show
        requests.post(url)
    except Exception as ex:
        print('BarkMe Error:' + str(ex))

def ReadConfigIni():
    cf = configparser.ConfigParser()
    cf.read("config.ini", encoding="utf-8")
    configInfo = ConfigInfo()
    # 下载的根目录
    configInfo.saveRootPath = cf.get("DownloadConfig", "saveRootPath")
    # 并发数
    configInfo.concurrency = int(cf.get("DownloadConfig", "concurrency"))
    # Bark Url
    configInfo.barkurl = 'https://baidu.com'
    # Bark apikey
    configInfo.barkapikey = '1234567'
    # Notity Url
    configInfo.notifyurl = 'https://www.baidu.com'
    # 重复的次数，-1 是一直循环
    configInfo.repeatTimes = 1
    # 重复的间隔 5h
    configInfo.delay = 5 * 3600

    configInfo.barkurl = cf.get("BarkConfig", "barkurl")
    configInfo.barkapikey = cf.get("BarkConfig", "barkapikey")
    configInfo.notifyurl = cf.get("BarkConfig", "notifyurl")
    configInfo.repeatTimes = int(cf.get("DownloadConfig", "repeatTimes"))
    configInfo.delay = int(cf.get("DownloadConfig", "delay"))

    return configInfo

if __name__ == '__main__':
    # --------------------------------------------------------------
    # 读取外部配置
    configInfo = ReadConfigIni()

    while configInfo.repeatTimes > 0 or configInfo.repeatTimes == -1:
        logger = LogHelper('Bili', cmdLevel='INFO', fileLevel="DEBUG").logger

        try:
            logger.info('repeatTimes = ' + str(configInfo.repeatTimes))
            # --------------------------------------------------------------
            # 设置需要下载的信息
            # 每个 UP 主视频
            downloadlistfile = 'DownloadList.txt'
            if os.path.exists(downloadlistfile) == True:
                filmList = ReadDownloadList(downloadlistfile)
            else:
                logger.error("DownloadList.txt not found")
                raise Exception("DownloadList.txt not found")

            uperList = ReadDownloadList(downloadlistfile)

            MainProcess(logger, uperList, configInfo.saveRootPath, configInfo.concurrency)

            BarkMe(configInfo.barkurl, configInfo.barkapikey, 'Job 4 Bilibli', configInfo.notifyurl)
        except Exception as ex:
            logger.error(ex)
        finally:
            logger.info('MainProcess One Time Done.')

        # 等待
        if configInfo.repeatTimes > 0:
            configInfo.repeatTimes = configInfo.repeatTimes - 1

        # 如果只是运行一次，那么就无需等待，马上退出
        if configInfo.repeatTimes == 0:
            pass
        else:
            try:
                CloseChrome()
            except expression as identifier:
                logger.error(ex)
            
            time.sleep(configInfo.delay)

    print("Done.")