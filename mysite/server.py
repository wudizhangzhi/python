#!/usr/bin/python
#coding=utf-8


from config import *
from db import mysql_cursor, redis_cursor
import tornado.web
from tornado.httpserver import HTTPServer
import tornado.ioloop



class BaseHanler(tornado.web.RequestHandler):
    '''
    基础类
    '''
    def __init__(self):
        pass



class IndexHandler(BaseHanler):
    '''
    主页
    大面积贴纸墙
    '''
    def get(self):
        self.render('templates/index.html')



class Applicaion(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler)
        ]
        super(Applicaion, self).__init__(
            handlers,
            static_path=static_path,
            template_path=template_path,
            login_url='/login',
            xsrf_cookies=True,
            debug=DEBUG,
            cookie_secret=cookie_secret,
        )
if __name__ == '__main__':
    app = HTTPServer(Applicaion, xheaders=True)
    app.listen(serverport)
    if DEBUG:
        print 'server start at %s' % serverport
    loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(loop)
    loop.start()
