#!/usr/bin/python
#coding=utf8

from threading import Thread
from bs4 import BeautifulSoup
from conndb import *
import re
import requests


'''
爬取用户和问题的url
redis 集合

zhihu_url_people:等待爬取的用户地址
zhihu_url_question:等待爬取的问题地址

mysql

zhihu_url_crawled:爬取过的地址(url_start)
'''
verify = False

class Url():
    def __init__(self, starturl):
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.zhihu.com',
            'Origin': 'http://www.zhihu.com',
            'Referer': 'http://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0 Accept: */*',
            'X-Requested-With': 'XMLHttpRequest'

        }
        self.session = requests.Session()
        self.session.headers.update(header)
        #起始地址
        self.url_start = starturl


    def _get(self, url):
        return self.session.get(url, verify=verify)


    def run(self):
        r = self._get(self.url_start)
        if r.status_code == requests.codes.OK:
            # 
            sql = 'insert into zhihu_url_crawled(url) values(%s)'
            db.execute(sql, self.url_start)

            soup = BeautifulSoup(r.content, 'lxml')
            question = set(self.find_question_url(soup))
            people = set(self.find_people_url(soup))

            pipe = redis_cache.pipeline()
            # 如果没有采集过,保存到redis
            question_save = []
            for q in question:
                if not redis_cache.sismember('zhihu_url_question', q):
                    sql = 'select id from zhihu_question where question_id=%s'
                    ret = db.query(sql, int(q))
                    if not ret:
                        question_save.append(q)
                        #pipe.sadd('zhihu_url_question', q)                    



            redis_cache.sadd('zhihu_url_question', *question_save)
            del question_save, question

            people_save = []
            for p in people:
                if not redis_cache.sismember('zhihu_url_people', p):
                    sql = 'select id from zhihu_user where urlname=%s'
                    ret = db.query(sql, int(q))
                    if not ret:
                        people_save.append(p)
                        #pipe.sadd('zhihu_url_people', q)  
            redis_cache.sadd('zhihu_url_people', *people_save)
            del people_save, people

            #pipe.execute()

            #添加值
            #sadd zhihu_url_people value1
            #判断是否存在
            #sismember zhihu_url_people value1
            #spop key
            #TODO 跟进url，继续匹配


        else:
            print r.status

    def find_question_url(self, soup):
        '''
        筛选问题地址
        '''
        r = []
        a = soup.find_all('a')
        for i in a:
            href = i.get('href')
            m = re.search(r'/question/(\d+)', str(href))
            if m:
                r.append(m.group()[-8:])
        return r

    def find_people_url(self, soup):
        '''
        筛选用户地址
        '''
        r = []
        a = soup.find_all('a')
        for i in a:
            href = i.get('href')
            m = re.search(r'/people/[^/]*', str(href))
            if m:
                r.append(m.group().split('/')[2])
        return r


if __name__ == '__main__':
    url = Url('https://www.zhihu.com/question/19977199')    
    url.run()

