import os
import sys
from you_get import common as you_get
from Common import CheckRedirectUrl

try:
    # kk = "www.bilibili.com/video/av70593729"
    kk = "www.bilibili.com/video/BV1QE411c73B"
    newll = CheckRedirectUrl(kk)

    directory = r"D:\Bilibili"
    fileName = '123'
    url = 'https://www.bilibili.com/bangumi/play/ep288525'
    sys.argv = ['you-get', '--debug', '-o', directory, '-O', fileName, newll]
    kk = you_get.main()
    print(kk)
except Exception as ex:
    print(ex)
    
    print(111)
