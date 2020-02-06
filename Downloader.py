import os
import sys
import re
from Common import CheckRedirectUrl
from you_get import common as you_get

class Downloader():
    def __init__(self, ilogger, idirectory, itime, ititle, iurl):
        super().__init__()
        self.logger = ilogger
        self.directory = idirectory
        self.time = itime
        self.title = ititle
        self.url = iurl

    def ProcessOne(self):
        try:
            # 去除特殊字符，否则下载文件会有问题
            fileName = re.sub('[\/:*?"<>|]','-', self.title)
            # self.newUrl = CheckRedirectUrl(self.url)
            # if self.newUrl is None:
            #     raise Exception("CheckRedirectUrl " + self.url + " Fail.")
            # else:
            #     self.newUrl = self.url
            self.newUrl = self.url
            sys.argv = ['you-get','--debug', '-o', self.directory, '-O', self.time + "_" + fileName, self.newUrl]
            self.logger.info("start download " + fileName + " -- " +  self.newUrl)
            you_get.main()
            self.logger.info("end download")
            return True
        except Exception as ex:
            self.logger.error("Downloader Error: " + fileName + " -- " +  self.url + ' -- newUrl: ' + self.newUrl)
            return False
