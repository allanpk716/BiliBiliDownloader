# -*- coding: utf-8 -*-
from ruia import Middleware
import fakeagent

middleware = Middleware()

@middleware.request
async def print_on_request(spider_ins, request):
    request.headers.update({'User-Agent': fakeagent.ua.random})