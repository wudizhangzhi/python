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

if __name__ == '__main__':
    question = Question()
    question.run()