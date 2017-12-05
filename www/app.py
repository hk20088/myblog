#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Leon Hu'

'''
async web application.
'''

import logging;

logging.basicConfig(level=logging.INFO)
import asyncio

from aiohttp import web

'''
定义首页返回 hello world...,注意需要加上 content_type='text/html'  ， 否则浏览器可能直接下载网页
'''


def index(request):
    return web.Response(body=b'<h1>hello world...</h1>', content_type='text/html')


'''
/hello/name 根据name的值返回 hello,name!
'''


def hello(request):
    text = '<h1>hello,%s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'), content_type='text/html')


'''
初始化函数， 也是个coroutine(协程)
'''


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    # loop.create_server()则利用asyncio创建TCP服务。
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at 127.0.0.1:9000')
    return srv


# 获取EventLoop
loop = asyncio.get_event_loop()
# 执行coroutine
loop.run_until_complete(init(loop))
loop.run_forever()
