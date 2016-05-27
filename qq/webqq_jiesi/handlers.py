# coding=utf-8
__author__ = 'Administrator'

import sys, json, os, threading

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

import tornado.web, tornado.escape, tornado.websocket,time
from tornado.web import UIModule
from db import mydb
from lib.QQcopy import QQ

db_ = mydb()


class baseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('cookieName')

    def write_error(self, status_code, **kwargs):
        print 'error:' + str(status_code)
        if status_code == 404:
            self.render('404.html', )
        elif status_code == 500:
            self.render('404.html')
        else:
            super(baseHandler, self).write_error(status_code, **kwargs)

class nopageHandler(baseHandler):
    '''没有被收集到的错误默认为404'''

    def get(self, *args, **kwargs):
        print 'nopage'
        raise tornado.web.HTTPError(404)

class mainThread(threading.Thread):
    def __init__(self, filename):
        super(mainThread, self).__init__()
        self.isStop = False
        self.filename = filename
        self.q = QQ()

    def run(self):
        def runQQ(filename):
            self.q.run(filename)

        subthread = threading.Thread(target=runQQ, args=(self.filename,))
        subthread.setDaemon(True)
        subthread.start()
        print u'子线程开始'
        # while True:
        #     if self.getQQ()!=None:
        #
        #         break

    def stop(self):
        print 'stop'
        self.isStop = True

    def getQQ(self):
        print 'getQQ'
        return self.q.getQQnumber()


working = {}

class QQLoginhandler(baseHandler):
    '''webqq登录页面'''
    def __init__(self, application, request, **kwargs):
        super(QQLoginhandler, self).__init__(application, request, **kwargs)
        self.pro=None

    def get(self, *args, **kwargs):
        print 'qqlogin get'
        # TODO 每刷新一次都需要等上一个线程自动停止。如何控制子线程停止???
        # TODO 目前设置子线程20次循环检查后退出
        # 设置唯一的二维码文件名
        print str(id(self))
        rqname = str(id(self))+'.png'
        self.render("webqqlogin.html", rqname=rqname)
        t = mainThread(rqname)
        t.start()
        t.join()
        working[rqname] = t
        print u'绑定线程'

    def post(self, *args, **kwargs):
        print 'webqqlogin post'
        # 获得QQ号码并转页
        rqnum = self.get_argument('rqnum')
        rqnum = rqnum.split('/')[-1]
        t = working[rqnum]
        qqnumber = str(t.getQQ()[0])
        self.set_cookie('qqnum', qqnumber)
        self.set_cookie('username', str(t.getQQ()[1]))
        working.pop(rqnum)


class QQmsghandler(baseHandler):
    '''QQ消息显示页面'''

    def get(self, *args, **kwargs):
        qqnum = self.get_cookie('qqnum')
        username = self.get_cookie('username')
        #测试
        # username=u'盛夏光年'
        # qqnum='2634107307'
        d_ = mydb()
        sql = 'SELECT * FROM webqq_msg WHERE to_uin=' + qqnum + ' ORDER BY id DESC;'
        msgs = d_.select(sql)
        self.render('qqshowmsg.html', msgs=msgs, username=username)

    def post(self, *args, **kwargs):
        searchword = self.get_argument('searchword')
        searchword='%'+searchword+'%'
        d_ = mydb()
        # qqnum = self.get_cookie('qqnum')
        qqnum='2634107307'
        sql = 'SELECT * FROM webqq_msg WHERE to_uin=' + qqnum + ' AND content LIKE %s ORDER BY id DESC;'
        msgs = d_.select(sql,searchword)
        # if len(searchword) == 0 or searchword==None:
        #     self.render('qqmsg.html', msgs=msgs)
        #     return
        # msgs = fuzzyfinder(searchword, msgs)
        print u'搜索：' + searchword + u',搜索结果数目：' + str(len(msgs))
        self.render('qqmsg.html', msgs=msgs)


class QQmsg_page_handler(baseHandler):
    '''页码'''
    def get(self, *args, **kwargs):
        pass
    def post(self, *args, **kwargs):
        pass

class msg_time_UIModule(UIModule):
    '''qq消息时间模板'''
    def render(self, t):
        t=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
        return t


class msgUIModule(UIModule):
    '''qq消息内容模板'''
    def render(self, msg):
        return msg
