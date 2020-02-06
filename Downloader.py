import os
import sys
import re
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
            sys.argv = ['you-get','--debug', '-o', self.directory, '-O', self.time + "_" + fileName, self.url]
            self.logger.info("start download " + fileName + " -- " +  self.url)
            you_get.main()
            self.logger.info("end download")
            return True
        except Exception as ex:
            self.logger.error("Downloader Error: " + fileName + " -- " +  self.url)
            return False
