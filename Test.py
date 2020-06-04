import os
import sys
import re
from you_get import common as you_get
from Common import CheckRedirectUrl


repattern = r"\d{4}-\d{2}-\d{2}_"

try:
    sour = '123456'
    desDir = {}
    desDir['2020-06-01_1213456'] = 0
    desDir['2020-06-02_1223456'] = 0
    desDir['2020-06-03_123456'] = 0
    desDir['2020-06-04_12533456'] = 0
    desDir['2020-06-05_12253456'] = 0
    desDir['567123456'] = 1
    desDir['2020-06-01_123456'] = 0
    
    if any(filter(lambda d: d.split('_')[-1] == sour, desDir.keys())):
        print('1')
    else:
        print('0')
        
    if any(filter(lambda d: d.replace(re.findall(repattern, d, flags=0)[0], '') == sour, desDir.keys())):
        print('1')
    else:
        print('0')

    print('Done')


    # if len(list(filter(lambda d: d.replace(re.findall(repattern, d, flags=0)[0], '') == sour, desDir.keys()))) > 0:
    #     print(1)
    # else:
    #     print(0)

    # if sour in desDir.keys():
    #     print(1)
    # else:
    #     print(0)

    


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
