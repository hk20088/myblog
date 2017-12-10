#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Leon Hu'

'''
async web application.
'''

import logging;
logging.basicConfig(level=logging.INFO)
import asyncio
import os
import time
import datetime
import www.orm as orm

from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from www.coroweb import add_routes, add_static
from www.config import configs


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


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    # 初始化模板配置，包括模板运行代码的开始和结束标识符，变量的开始和结束标识符
    options = dict(
        # 是否转义设置为True，就是在渲染模板时自动把变量中的<>&等字符转换为&lt;&gt;&amp;
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),  # 运行代码的开始标识符
        block_end_string = kw.get('block_end_string', '%}'),  # 运行代码的结束标识符
        variable_start_string = kw.get('variable_start_string', '{{'),  # 变量开始标识符
        variable_end_string = kw.get('variable_end_string', '}}'),  # 变量结束标识符
        # Jinja2会在使用Template时检查模板文件的状态，如果模板有修改， 则重新加载模板。如果对性能要求较高，可以将此值设为False
        auto_reload = kw.get('auto_reload', True)

    )
    # 从参数中获取path的位置，即模板文件的位置
    path = kw.get('path', None)
    # 如果没有，则默认为当前文件目录下的 templates 目录
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

    logging.info('set jinja2 template path: %s' % path)
    # Environment是Jinja2中的一个核心类，它的实例用来保存配置、全局对象，以及从本地文件系统或其它位置加载模板。
    # 这里把要加载的模板和配置传给Environment，生成Environment实例
    env = Environment(loader=FileSystemLoader(path), **options)

    # 从参数取filter字段
    # filters: 一个字典描述的filters过滤器集合, 如果非模板被加载的时候, 可以安全的添加filters或移除较早的.
    filters = kw.get('filters', None)
    # 如果有传入的过滤器设置，则设置为env的过滤器集合
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    # 给webapp设置模板
    app['__templating__'] = env

# ------------------------------------------拦截器middlewares设置-------------------------

@asyncio.coroutine
def logger_factory(app, handler):  # 在正式处理之前打印日志
    @asyncio.coroutine
    def logger(request):
        logging.info('Requst : %s, %s' % (request.method, request.path))
        return (yield from handler(request))
    return logger


@asyncio.coroutine
def data_factory(app, handler):
    @asyncio.coroutine
    def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = yield from request.json()
                logging.info('request json : %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = yield from request.post()
                logging.info('request form : %s' % str(request.__data__))
        return (yield from handler(request))
    return parse_data

# 是为了验证当前的这个请求用户是否在登录状态下，或是否是伪造的sha1
# @asyncio.coroutine
# def auth_factory(app, handler):
#     @asyncio.coroutine
#     def auth(request):
#         logging.info('check user: %s %s' % (request.method, request.path))
#         request.__user__ = None
#         # 获取到cookie字符串
#         cookie_str = request.cookies.get(COOKIE_NAME)
#         if cookie_str:
#             # 通过反向解析字符串和与数据库对比获取出user
#             user = yield from cookie2user(cookie_str)
#             if user:
#                 logging.info('set current user: %s' % user.email)
#                 # user存在则绑定到request上，说明当前用户是合法的
#                 request.__user__ = user
#         if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
#             return web.HTTPFound('/signin')
#         # 执行下一步
#         return (yield from handler(request))
#     return auth

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


'''
初始化函数， 也是个coroutine(协程)
'''
@asyncio.coroutine
def init(loop):
    # 创建数据库连接池，db参数传配置文件里的配置db
    yield from orm.create_pool(loop=loop, **configs.db)

    # middlewares设置两个中间处理函数
    # middlewares中的每个factory接受两个参数，app 和 handler(即middlewares中的下一个元素)
    # 譬如这里logger_factory的handler参数其实就是response_factory()
    # middlewares的最后一个元素的Handler会通过routes查找到相应的，其实就是routes注册的对应handler
    app = web.Application(loop=loop, middlewares=[logger_factory])
    # 初始化jinja2模板
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)

    # loop.create_server()则利用asyncio创建TCP服务。
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at 127.0.0.1:9000')
    return srv


# 获取EventLoop
loop = asyncio.get_event_loop()
# 执行coroutine
loop.run_until_complete(init(loop))
loop.run_forever()
