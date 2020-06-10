# -*- coding: utf-8 -*-
import os
import fake_useragent

nowdirs = os.path.join(os.getcwd(), 'fake_agent') 
location = os.path.join(nowdirs, 'fake_useragent%s.json' % fake_useragent.VERSION) 
ua = fake_useragent.UserAgent(path=location, cache=True)
