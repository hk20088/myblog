/*
Navicat MySQL Data Transfer

Source Server         : 本机
Source Server Version : 50720
Source Host           : localhost:3306
Source Database       : awesome

Target Server Type    : MYSQL
Target Server Version : 50720
File Encoding         : 65001

Date: 2017-12-20 10:46:27
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for blogs
-- ----------------------------
DROP TABLE IF EXISTS `blogs`;
CREATE TABLE `blogs` (
  `id` varchar(50) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_image` varchar(500) NOT NULL,
  `name` varchar(50) NOT NULL,
  `summary` varchar(200) NOT NULL,
  `content` mediumtext NOT NULL,
  `created_at` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blogs
-- ----------------------------
INSERT INTO `blogs` VALUES ('00151324608507167ca5c47176b4c75859862acd1c8e21c000', '00151322958275921414e71467e4316be4daaab58c07c8b000', 'Leon', 'http://www.gravatar.com/avatar/cdff51b61ab0c3f3c78167703163f0e3?d=mm&s=120', 'MyBlog开发总结', '根据廖大大的教程，从零开始，开发出这个博客，这里是开发总结。', '---\n# 前言\n\n**项目演示地址：**  [点击查看](http://www.baidu.com)   \n**管理员账户：** admin@admin.com  / 123456  \n*管理员账户拥有后台管理的权限，包括博客、评论和用户管理。为便于维护，这里禁用了管理员删除博客和评论的权限。*\n\n**普通账户：** test@test.com  / 123456  \n*普通账户可以阅读，评论博客*\n\n***\n在演示的过程中如果发现BUG或者你认为可以改进的地方，欢迎在GitHub中发起 pul request   \n另外欢迎大家创建博客，添加评论\n***\n\n● 使用Python3.6.0开发的个人博客项目，主要包含日志、用户和评论三大部分。  \n● 后续会不断完善或添加此项目的细节内容及功能，欢迎大家一起交流。  \n● 如果你喜欢这个项目，或者觉得对你有所帮助，可以点击右上解的 Star，Fork 按钮表示支持。  \n*另：*  \n● 项目基本按照 [廖雪峰的Python教程](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)实战来实现，廖老师的教程由浅入深，从零开始，一步步到最后的项目实战，通俗易懂，一气呵成，是个不可多得的学习Python的教程，推荐想学习Python的童鞋关注。  \n● 参考了[Pure](https://github.com/KaimingWan/PureBlog)的源代码及思路，受益匪浅，这里一并表示感谢    \n  \n\n# 准备工作\n1、安装 ``Python3.0`` 及以上版本（Python安装成功后，默认安装了 ``pip3``）  \n2、安装 ``aiohttp``, ``jinja2``, ``aiomysql``  \n3、安装 ``MySql5.x``数据库  \n4、安装几个第三方包的命令  \n\n`` pip install aiphttp     　　\n pip install jinja2  　  　\npip install aiomysql``  　　  \n\n\n# 代码结构\n备注：项目使用的markdown模块不支持输入代码标签，为了以更好的排版方式查看结构，可将此文复制到其它markdown工具中查看  \n[查看源码，对照代码结构](https://github.com/hk20088/myblog)  \n\nwww  \n　- static:存放静态资源，这里使用 UIkit作为前端框架  \n\n　- templates:存放模板文件  \n　　-` __base__.html`: 父模板，定义了页面中公共的属性，其它页面继承此页面  \n　　- blog.html: 单篇博客页面，包括博客内容及评论  \n　　- blogs.html: 博客列表，即首页  \n　　- `manage_blog_edit.html`: 添加博客页面  \n　　- `manage_blog_modify.html`: 修改博客页面  \n　　- `manage_blogs.html`: 博客管理页面，包括修改和删除博客  \n　　- `manage_comments.html`: 评论管理页面，超级管理员可删除评论  \n　　- `manage_users.html`: 用户管理页面  \n　　- register.html: 用户注册页面  \n　　- signin.html: 用户登录页面    \n　　- test.html: 测试页面，用来展示所有用户  \n\n　- apis.py: 定义几个错误异常类和Page类用于分页  \n　- app.py: HTTP服务器以及处理HTTP请求；拦截器、jinja2模板、URL处理函数注册等  \n　- config.py:默认和自定义配置文件合并  \n　- `config_default.py`:默认的配置文件信息  \n　- `config_override.py`:自定义的配置文件信息  \n　- coroweb.py: 封装aiohttp，即写个装饰器更好的从Request对象获取参数和返回Response对象  \n　- handlers.py: Web API模块，项目所有的API都在此模块完成  \n　- markdown2.py:支持markdown显示的插件   \n　- models.py: 实体类  \n　- orm.py: ORM框架  \n　- tesp.py: 用于测试orm框架的测试模块  \n\n# 核心模块\n## orm.py实现思路\n● 实现ModelMetaclass，主要完成类属性域和特殊变量直接的映射关系，方便Model类中使用。同时可以定义一些默认的SQL处理语句  \n● 实现Model类,包含基本的get,set方法用于获取和设置变量域的值。Model从dict继承，拥有dict的所有功能。  \n同时实现相应的SQL处理函数（这时候可以利用ModelMetaclass自动根据类实例封装好的特殊变量)  \n● 实现基本的数据库类型类，在应用层用户只要使用这种数据库类型类即可，避免直接使用数据的类型增加问题复杂度  \n\n## coroweb.py实现思路\nweb框架在此处主要用于对aiohttp库的方法做更高层次的封装，用于抽离一些可复用的代码，从而简化操作。主要涉及的封装内容为：  \n\n● 定义装饰器@get()和@post()用与自动获取URL路径中的基本信息  \n● 定义RequestHandler类，该类的实例对象获取完整的URL参数信息并且调用对应的URL处理函数（类中的方法）  \n● 定义`add_router`方法用于注册对应的方法，即找到合适的fn给`app.router.add_route()`方法。该方法是aiohttp提供的接口，用于指定URL处理函数  \n\n综上，处理一个请求的过程即为：\n\n● app.py中注册所有处理函数、初始化jinja2、添加静态文件路径  \n● 创建服务器监听线程  \n● 收到一个request请求  \n● 经过几个拦截器(middlewares)的处理(app.py中的app = web.Application..这条语句指定)  \n● 调用RequestHandler实例中的 ``__call__`` 方法；再调用``__call__``方法中的post或者get方法  \n● 从已经注册过的URL处理函数中(handler.py)中获取对应的URL处理方法  \n\n# 遇到的问题\n● 连接数据库时的编码问题  \ncharset=kw.get(\'charset\', \'utf8\')这里的 utf8 习惯性写成 utf-8 ，造成编码异常  \n\n# 参考资料\n[廖大大官网](https://www.liaoxuefeng.com/)  \n[Pure的GitHub](https://github.com/KaimingWan)  \n[uikit](http://www.getuikit.net/index.html)  \n[VUE](https://cn.vuejs.org/)  ', '1513246085.07134');
INSERT INTO `blogs` VALUES ('001513330865615176cbb6490a54efd9f7d4d3d0874844a000', '00151322958275921414e71467e4316be4daaab58c07c8b000', 'Leon', 'http://www.gravatar.com/avatar/cdff51b61ab0c3f3c78167703163f0e3?d=mm&s=120', '360 宣布永久关闭水滴直播平台 将聚焦安防监控', '360 宣布永久关闭水滴直播平台 将聚焦安防监控', '12 月 20 日上午消息，360 公司于今日宣布主动、永久关闭水滴直播平台 ... 水滴直播相关负责人表示，水滴直播本身是一个响应用户需求而出现的创新产品，在这个过程中，水滴直播平台的一些功能存在争议，也存在被恶意利用的可能 ... 直播与安防监控，在 360 智能摄像机上完全是两件事，绝大部分摄像机的用户都是用来做监控的，做直播的用户，需要经过数道复杂的流程才能发布直播。', '1513330865.61588');
INSERT INTO `blogs` VALUES ('0015133308797068e5760f33a0b4ae58687b20c28376f02000', '00151322958275921414e71467e4316be4daaab58c07c8b000', 'Leon', 'http://www.gravatar.com/avatar/cdff51b61ab0c3f3c78167703163f0e3?d=mm&s=120', 'YouTube 结盟三大唱片公司 新音乐服务将上线', 'YouTube 结盟三大唱片公司 新音乐服务将上线', 'YouTube 计划推出的收费音乐服务 Remix，将是 Alphabet 为追赶竞争对手 Spotify 和苹果第三次尝试付费音乐服务 ... Spotify 和苹果音乐等付费音乐服务让陷入近 20 年低迷的全球音乐产业实现了复兴，但一些主流唱片公司依旧表示，如果不是 YouTube，他们的收入还将会更高 ... 除去三大唱片公司外，YouTube 还在与 Vevo 谈判，后者负责为环球唱片和索尼唱片分发音乐视频。', '1513330879.70668');


-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `passwd` varchar(50) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image` varchar(500) NOT NULL,
  `created_at` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_email` (`email`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('0015132240044558e7077bbf886463189af7c87b4207ca4000', 'test@test.com', '5f4c04f55461a0ee82c7096a5008482101129ab1', '0', 'test', 'http://www.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=mm&s=120', '1513224004.4553');
INSERT INTO `users` VALUES ('0015132240285617488c0a64c33481ebe9aa819d5cdbce1000', 'admin@admin.com', '3f9bfddb3fea3f3cd9d40d196af9c7f1ae473e8b', '1', 'admin', 'http://www.gravatar.com/avatar/64e1b8d34f425d19e1ee2ea7236d3028?d=mm&s=120', '1513224028.56168');
INSERT INTO `users` VALUES ('00151322958275921414e71467e4316be4daaab58c07c8b000', 'leon@leon.com', '3e09875f3af8db728519e12d5c929254e2984854', '1', 'Leon', 'http://www.gravatar.com/avatar/cdff51b61ab0c3f3c78167703163f0e3?d=mm&s=120', '1513229582.7594');
