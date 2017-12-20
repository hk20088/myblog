# 前言
**项目演示地址：** [点击查看](http://117.79.147.222:9000)
**管理员账户：** admin@admin.com / 123456
*管理员账户拥有后台管理的权限，包括博客、评论和用户管理。为便于维护，这里禁用了管理员删除博客和评论的权限。*

**普通账户：** test@test.com / 123456
*普通账户可以阅读，评论博客*

***在演示的过程中如果发现BUG或者你认为可以改进的地方，欢迎发起 pul request***

● 使用Python3.6.0开发的个人博客项目，主要包含日志、用户和评论三大部分。
● 后续会不断完善或添加此项目的细节内容及功能，欢迎大家一起交流。
● 如果你喜欢这个项目，或者觉得对你有所帮助，可以点击右上解的 Star，Fork 按钮表示支持。
*另：  *
● 项目基本按照 <廖雪峰的Python教程>实战来实现，廖老师的教程由浅入深，从零开始，一步步到最后的项目实战，通俗易懂，一气呵成，是个不可多得的学习Python的教程，推荐想学习Python的童鞋关注。
● 参考了 Pure的源代码及思路，受益匪浅，这里一并表示感谢


# 准备工作
1、安装 Python3.0 及以上版本（Python安装成功后，默认安装了 pip3）
2、安装 aiohttp, jinja2, aiomysql
3、安装 MySql5.x数据库
4、安装几个第三方包的命令
> pip install aiphttp
> pip install jinja2
> pip install mysql

# 代码结构
```
www
    - sql: 存放项目用到的sql脚本
        - awesome.sql: 数据初始化脚本
        - myblog.sql: 建库脚本（先执行此脚本）
	- static:存放静态资源，这里使用 UIkit作为前端框架
	- templates:存放模板文件
	    - __base__.html: 父模板，定义了页面中公共的属性，其它页面继承此页面
	    - blog.html: 单篇博客页面，包括博客内容及评论
	    - blogs.html: 博客列表，即首页
	    - manage_blog_edit.html: 添加博客页面
	    - manage_blog_modify.html: 修改博客页面
	    - manage_blogs.html: 博客管理页面，包括修改和删除博客
	    - manage_comments.html: 评论管理页面，超级管理员可删除评论
	    - manage_users.html: 用户管理页面
	    - register.html: 用户注册页面
	    - signin.html: 用户登录页面
	    - test.html: 测试页面，用来展示所有用户
	- apis.py: 定义几个错误异常类和Page类用于分页
	- app.py: HTTP服务器以及处理HTTP请求；拦截器、jinja2模板、URL处理函数注册等
	- config.py:默认和自定义配置文件合并
	- config_default.py:默认的配置文件信息
	- config_override.py:自定义的配置文件信息
	- coroweb.py: 封装aiohttp，即写个装饰器更好的从Request对象获取参数和返回Response对象
	- handlers.py: Web API模块，项目所有的API都在此模块完成
	- markdown2.py:支持markdown显示的插件
	- models.py: 实体类
	- orm.py: ORM框架
	- pymonitor.py 文件改动后，自动重启服务
	- tesp.py: 用于测试orm框架的测试模块
```

# 核心模块
## orm.py实现思路
● 实现ModelMetaclass，主要完成类属性域和特殊变量直接的映射关系，方便Model类中使用。同时可以定义一些默认的SQL处理语句
● 实现Model类,包含基本的get,set方法用于获取和设置变量域的值。Model从dict继承，拥有dict的所有功能。
同时实现相应的SQL处理函数（这时候可以利用ModelMetaclass自动根据类实例封装好的特殊变量)
● 实现基本的数据库类型类，在应用层用户只要使用这种数据库类型类即可，避免直接使用数据的类型增加问题复杂度

## coroweb.py实现思路
web框架在此处主要用于对aiohttp库的方法做更高层次的封装，用于抽离一些可复用的代码，从而简化操作。主要涉及的封装内容为：

● 定义装饰器@get()和@post()用与自动获取URL路径中的基本信息
● 定义RequestHandler类，该类的实例对象获取完整的URL参数信息并且调用对应的URL处理函数（类中的方法）
● 定义add_router方法用于注册对应的方法，即找到合适的fn给app.router.add_route()方法。该方法是aiohttp提供的接口，用于指定URL处理函数

综上，处理一个请求的过程即为：

● app.py中注册所有处理函数、初始化jinja2、添加静态文件路径
● 创建服务器监听线程
● 收到一个request请求
● 经过几个拦截器(middlewares)的处理(app.py中的app = web.Application..这条语句指定)
● 调用RequestHandler实例中的__call__方法；再调用__call__方法中的post或者get方法
● 从已经注册过的URL处理函数中(handler.py)中获取对应的URL处理方法

# 遇到的问题
● 连接数据库时的编码问题
charset=kw.get('charset', 'utf8')这里的 utf8 习惯性写成 utf-8 ，造成编码异常

# 参考资料
[廖大大官网](https://www.liaoxuefeng.com/)
[Pure的GitHub](https://github.com/KaimingWan)
[uikit](http://www.getuikit.net/index.html)
[VUE](https://cn.vuejs.org/)


