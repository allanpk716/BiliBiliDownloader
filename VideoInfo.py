# -*- coding: utf-8 -*-
class VideoInfo():
    def __init__(self, iurl):
        super().__init__()
        self.time = ''
        self.title = ''
        self.url = iurl
        # 包含后缀名
        self.loaclFileName = ''
        self.isDownloaded = False