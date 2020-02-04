# -*- coding: utf-8 -*-
from ruia import Middleware
from fake_useragent import UserAgent

ua = UserAgent()
middleware = Middleware()

@middleware.request
async def print_on_request(spider_ins, request):
    request.headers.update({'User-Agent': ua.random})