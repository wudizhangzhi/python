#!/usr/bin/python
#coding=utf8

import threading
from zhihu import ZhiHu
from conndb import *
import time

'''
从redis取出用户地址进行爬取
'''

class People():
    def __init__(self):
        self.client = ZhiHu()
        pass

    def run(self):
        while True:
            r = redis_cache.rpop('zhihu_url_people')
            if r:
                url = 'https://www.zhihu.com/people/' + r
                self.client.user(url)

                print r
            time.sleep(1)
        pass


if __name__ == '__main__':
    people = People()
    people.run()
