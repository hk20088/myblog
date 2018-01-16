#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Leon Hu'

'''URL handlers'''

import logging;
logging.basicConfig(level=logging.INFO)
import time
import asyncio
import hashlib
import re
import json
import markdown2

from aiohttp import web
from coroweb import get, post
from models import User, Blog, Comment, next_id
from config import configs
from apis import APIValueError, APIPermissionError, APIError, APIResourceNotFoundError, Page

# 判断当前用户是否是管理员
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

# 获取页数，主要做一些容错处理
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

# 把纯文本文件转为html格式的文本
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

@get('/')
async def index(*, page='1'):
    # summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    # blogs = [
    #     Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
    #     Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
    #     Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    # ]

    # 获取到要展示的博客页数是第几页
    page_index = get_page_index(page)
    # 查找博客表里的条目数
    num = await Blog.findNumber('count(id)')
    # 通过Page类来计算当前页的相关信息
    page = Page(num, page_index)
    # 如果表里没有条目，则不需要系那是
    if num == 0:
        blogs = []
    else:
        # 否则，根据计算出来的offset(取的初始条目index)和limit(取的条数)，来取出条目
        blogs = await Blog.findAll(orderBy='priority desc,created_at desc', limit=(page.offset, page.limit))
        # 返回给浏览器
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs
    }

# ------------------------------------------生成cookie及解析cookie的函数--------------------------------- #

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

# 根据用户信息，拼接一个cookie字符串
def user2cookie(user, max_age):
    # 过期时间是当前时间+设置的有效时间
    expires = str(int(time.time() + max_age))
    # 构建cookie存储的字符串信息
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    # 将L用 - 隔开并返回
    return '-'.join(L)


# 根据cookie字符串，解析出用户相关信息
@asyncio.coroutine
def cookie2user(cookie_str):
    # cookie_str是空则返回
    if not cookie_str:
        return None
    try:
        # 通过'-'分割字符串
        L = cookie_str.split('-')
        # 如果不是3个元素的话，与我们当初构造sha1字符串时不符，返回None
        if len(L) != 3:
            return None
        # 分别获取到用户id，过期时间和sha1字符串
        uid, expires, sha1 = L
        # 如果超时，返回None
        if int(expires) < time.time():
            return None
        # 根据用户id查找库，对比有没有该用户
        user = yield from User.find(uid)
        # 没有该用户返回None
        if user is None:
            return None
        # 根据查到的user的数据构造一个校验sha1字符串
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        # 比较cookie里的sha1和校验sha1，一样的话，说明当前请求的用户是合法的
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        # 返回合法的user
        return user
    except Exception as e:
        logging.exception(e)
        return None

# ------------------------------------------用户登录登出及注册处理函数---------------------------------------#

@get('/register')
def register():
    return {
        '__template__':'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__':'signin.html'
    }

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    # 清理掉cookie的用户信息数据
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out')
    return r


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

# 注册时，服务器收到的密码是在客户端经过SHA加密过的密码，并且加密时用email加了盐
# 在将密码存入数据库时， 以uid为盐，再次将password进行SHA加密
# 所以即使两个用户的密码是相同的， 保存到数据库时生成的密码字符串也是不一样的
@post('/api/userRegister')
@asyncio.coroutine
def api_register_user(*, email, name, passwd):
    # 判断name是否存在，且是否只是'\n', '\r',  '\t',  ' '，这种特殊字符
    if not name or not name.strip() or name.lower() == 'leon':
        raise APIValueError('name')
    # 判断email是否存在，且是否符合规定的正则表达式
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    # 判断passwd是否存在，且是否符合规定的正则表达式
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')

    # 查一下库里是否有相同的email地址，如果有的话提示用户email已经被注册过
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in used.')

    # 生成一个当前要注册用户的唯一uid
    uid = next_id()
    # 构建shal_passwd
    sha1_passwd = '%s:%s' % (uid, passwd)

    admin = False
    if email == 'admin@163.com':
        admin = True

    # 创建一个用户，密码是用sha1加密保存
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest(),
                admin=admin)
    # 保存这个用户到数据库
    yield from user.save()
    logging.info('save user ok...')
    # 构建返回信息
    r = web.Response()

    # 添加cookie
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # 把密码改为 ******，以避免返回的时候暴露
    user.passwd = '******'
    r.content_type = 'application/json'
    # 把对象转换了json格式返回
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


# 登录请求，切记， 同一个模块不可以有重名的函数
@post('/api/authenticate')
@asyncio.coroutine
def authenticate(*, email, passwd):
    # 如果email或passwd为空，都说明有错误
    if not email:
        raise APIValueError('email', 'Invalid email')
    if not passwd:
        raise APIValueError('passwd', 'Invalid  passwd')
    # 根据email在库里查找匹配的用户
    users = yield from User.findAll('email=?', [email])
    # 没找到用户，返回用户不存在
    if len(users) == 0:
        raise APIValueError('email', 'email not exist')
    # 取第一个查到用户，理论上就一个
    user = users[0]
    # 按存储密码的方式，取出传入的密码的hash值
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    # 和库里的密码字段的值作比较，一样的话认证成功，不一样的话，认证失败
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid passwd')

    # 构建返回信息
    r = web.Response()
    # 添加cookie
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
    user.passwd = '******'
    # 返回的是json数据，所以设置content-type为json的
    r.content_type = 'application/json'
    # 把对象转换成json格式返回
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


# ----------------------------------------用户管理的处理函数------------------------------------------#

# 获取所有用户
@get('/manage/users')
def manage_user(*, page='1'):
    return {
        '__template__':'manage_users.html',
        'page_index':get_page_index(page)
    }

@get('/api/users')
async def api_get_users(*, page='1'):
    # 返回所有的用户信息json格式
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'

    return dict(page=p, users=users)





# ----------------------------------------博客管理的处理函数-----------------------------------------#

# 管理首页，重写向到评论管理
@get('/manage')
def manage():
    return 'redirect:/manage/blogs'

# 跳到写博客的页面
@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__':'manage_blog_edit.html',
        'id':'',
        'action':'/api/blogs'  # 对应Html中VUE的action名字
    }

# 跳到博客管理页面（可修改，删除博客）
@get('/manage/blogs')
def manage_blogs(page='1', **kw):
    return {
        '__template__':'manage_blogs.html',
        'page_index':get_page_index(page)
    }

# 跳到博客修改页面
@get('/manage/blogs/modify/{id}')
def manage_modify_blog(id):
    return {
        '__template__': 'manage_blog_modify.html',
        'id': id,
        'action': '/api/blogs/modify'
    }

# 修改博客信息
@post('/api/blogs/modify')
@asyncio.coroutine
def api_modify_blog(id, name, summary, content,**kw):  # 这里用**kw接收blog对象的其它参数，否则会提示 TypeError异常
    # 修改一条博客
    logging.info("修改的博客的博客ID为：%s", id)
    # name，summary,content 不能为空
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    # 获取指定id的blog数据
    blog = yield from Blog.find(id)
    blog.name = name
    blog.summary = summary
    blog.content = content

    # 保存
    yield from blog.update()
    return blog



# 获取博客信息，包括此博客的评论
@get('/blog/{id}')
async def get_blog(id):
    # 根据博客ID，获取某篇博客信息
    blog = await Blog.find(id)

    # 根据博客id获取该条博客的评论
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')

    # markdown2是个扩展模块，这里把博客正文和评论套入到markdonw2中
    for c in comments:
        # c.html_content = text2html(c.content)
        c.html_content = markdown2.markdown(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


# 根据博客ID，获取某篇博客信息(用于修改博客时，获取博客信息)
@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog


# 获取博客列表
@get('/api/blogs')
@asyncio.coroutine
def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = yield from Blog.findAll(orderBy='priority desc,created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)



# 创建博客处理函数
@post('/api/blogs')
@asyncio.coroutine
def api_create_blog(request, *, name, summary, content):
    # 只有管理员才可以写日志
    check_admin(request)
    # name，summary,content 不能为空
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    # 根据传入的信息，构建一条博客数据
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    # 保存
    yield from blog.save()

    return blog



@post('/api/blogs/{id}/delete')
@asyncio.coroutine
def api_delete_blog(id, request):
    # 删除一条博客
    logging.info("删除博客的博客ID为：%s" % id)
    # 先检查是否是管理员操作，只有管理员才有删除博客权限
    check_admin(request)
    # 查询一下博客ID，数据库中是否有对应的博客
    b = yield from Blog.find(id)
    # 没有的话抛出错误
    if b is None:
        raise APIResourceNotFoundError('Blog')
    # 有的话删除
    yield from b.remove()
    return dict(id=id)

# ----------------------------------博客评论的处理函数------------------------------------#


# 获取所有评论
@get('/manage/comments')
def manage_comments(page='1', **kw):
    return {
        '__template__':'manage_comments.html',
        'page_index':get_page_index(page)
    }


@get('/api/comments')
async def api_get_comments(*, page='1'):
    page_index = get_page_index(page)
    # 查询总条数
    num = await Comment.findNumber('count(id)')
    # 拿到分页信息
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for c in comments:
        blog = await Blog.find(c.blog_id)
        c.blogName = blog.name
    return dict(page=p, comments=comments)


# 添加评论
@post('/api/blogs/{id}/comments')
@asyncio.coroutine
def api_create_comment(id, request, *, content):
    # 对某个博客发表评论
    user = request.__user__
    # 必须为登陆状态下，评论
    if user is None:
        raise APIPermissionError('content')
    # 评论不能为空
    if not content or not content.strip():
        raise APIValueError('content')
    # 查询一下博客id是否有对应的博客
    blog = yield from Blog.find(id)
    # 没有的话抛出错误
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    # 构建一条评论数据
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name,
                      user_image=user.image, content=content.strip())
    # 保存到评论表里
    yield from comment.save()
    return comment


# 删除评论
@post('/api/comments/{id}/delete')
async def api_delete_comment(id, request):
    # 校验是否是管理员，只有管理员才有删除评论的权限
    check_admin(request)
    logging.info("删除的评论ID是：%s" % id)

    # 检查数据库中是否有这条评论
    c = await Comment.find(id)
    # 如果没有则抛出异常
    if c is None:
        raise APIResourceNotFoundError('Comment')
    # 如果有则移除
    await c.remove()
    return dict(id=id)

