#!/usr/bin/python
#coding=utf8

import threading
from zhihu import ZhiHu
from conndb import *
import time


'''
从redis取出问题地址进行爬取
'''

class Question():
    def __init__(self):
        self.client = ZhiHu()
        pass

    def run(self):
        while True:
            r = redis_cache.spop('zhihu_url_question')
            if r:
                self.client.question(r)

                print '采集问题:%s' % r
            else:
                print 'wait'
            time.sleep(1)
        pass


class QuestionThread(threading.Thread):
    def __init__(self):
        #threading.Thread.__init__(self)
        super(QuestionThread, self).__init__()
        self.client = ZhiHu()

    def run(self):
        print 'thread is start running'
        r = redis_cache.spop('zhihu_url_question')
        if r:
            self.client.question(r)

            print '采集问题:%s' % r
        else:
            print 'wait'
        time.sleep(1)




