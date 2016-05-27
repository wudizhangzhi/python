# coding=utf-8
__author__ = 'Administrator'

import tornado.web
import tornado.ioloop
import tornado.autoreload
from handlers import *
from tornado.httpserver import HTTPServer

requestHandlers = [
    (r'/webqqlogin', QQLoginhandler),
    (r'/qqshowmsg', QQmsghandler),
    (r'.*', nopageHandler),
]

uiModule = {'msg_time_module': msg_time_UIModule,
            'msg_module': msgUIModule}

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'login_url': '/webqqlogin',
    'cookie_secret': '__TODO__type_in',
    'ui_modules': uiModule,
    # 'xsrf_cookies':True,
}
# app = tornado.web.Application(requestHandlers, **settings)
# httpserver = HTTPServer(app, xheaders=True)
# httpserver.bind(9001)
# httpserver.start(1)
# # app.listen(9001)
#
# tornado.ioloop.IOLoop.instance().start()


app = tornado.web.Application(requestHandlers, **settings)
app.listen(9001)
print 'start listen port 9001'
loop = tornado.ioloop.IOLoop.instance()
tornado.autoreload.start(loop)
loop.start()
