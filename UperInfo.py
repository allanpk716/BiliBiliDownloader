# -*- coding: utf-8 -*-
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