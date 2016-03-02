#!/usr/bin/python3
#coding=utf-8
import re
import requests
#from bs4 import beautifulsoup

url_target = 'https://www.zhihu.com/#signin'
url_login = 'https://www.zhihu.com/login/email'
s = requests.Session()
s.headers.update({
    'Accept':'*/*',
    'Accept-Encoding':'gzip,deflate,sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Host':'www.zhihu.com',
    'Origin':'http://www.zhihu.com',
    'Referer':'http://www.zhihu.com/',
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0 Accept: */*',
    'X-Requested-With':'XMLHttpRequest'

    })

r = s.get(url_target, verify=False)
_xsrf = re.findall('xsrf(.*)',r.text)[0][8:42]
data = {
    'email':'wudizhangzhi@163.com',
    'password':'zzc549527',
    '_xsrf':_xsrf,
    'remember_me':'true'
        }

r = s.post(url_login, data=data, verify=False)
print(r.status_code)
if r.json()['r'] == '0':
    print r.json()['msg']
print(r.content)

'''
伪码:
class zhihu():
    def __init__():
        self.session

    def login():
        #登录

    def num_followed(self, html):
        #分析html获取num
        return soup(html).find(...)

    def num_watched(self, html):
        return ....

    def follow_answer(self, html):
        #关注问题

    def url_matched_question(self, html):
        #获取符合规则的url地址
        #https://www.zhihu.com/question/34900989

    def url_matched_user(self, html):
        #获取用户url

    def question(self, html):
        #获取问题的具体数据：id， 题目，内容，最近活动时间,关注人数，浏览次数,回答数量

    def answer(self, html):
        #获取问题的答案，问题id，答题人， 回答内容，时间，赞同数量

'''

#一些设置
url_login_get = 'https://www.zhihu.com/#signin'
url_login_post = 'https://www.zhihu.com/login/email'
email = wudizhangzhi@163.com
passowrd = XXXXXXXXX
verify = False

class ZhiHu():
    def __init__(self):
        self.session = requests.Session()
        pass

    def login(self):
        r = self.session.get(url_login_get, verify=verify)
        _xsrf = re.findall('xsrf(.*)',r.text)[0][8:42]
        data = {
                'email':email,
                'password':password,
                '_xsrf':_xsrf,
                'remember_me':'true'
                }
        r = self.session.post(url_login_post, data=data, verify=verify)
        if r.json()['r'] == '0':
            print '登录成功'
        else:
            print '登录失败：%s', r.json()

    def _num_watched(self):


