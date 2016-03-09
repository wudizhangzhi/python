#!/usr/bin/python3
# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import re
import requests
from bs4 import BeautifulSoup
import torndb
import time


mysql_host = 'localhost'
mysql_db = 'zhihu'
mysql_user = 'root'
mysql_pass = 'admin'

db = torndb.Connection(mysql_host, mysql_db, user=mysql_user, password=mysql_pass)
# url_target = 'https://www.zhihu.com/#signin'
# url_login = 'https://www.zhihu.com/login/email'
# s = requests.Session()
# s.headers.update(
# {
#    'Accept':'*/*',
#    'Accept-Encoding':'gzip,deflate,sdch',
#    'Accept-Language':'zh-CN,zh;q=0.8',
#    'Connection':'keep-alive',
#    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
#    'Host':'www.zhihu.com',
#    'Origin':'http://www.zhihu.com',
#    'Referer':'http://www.zhihu.com/',
#    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0 Accept: */*',
#    'X-Requested-With':'XMLHttpRequest'
#
#    }
# )

# r = s.get(url_target, verify=False)
# _xsrf = re.findall('xsrf(.*)',r.text)[0][8:42]
# data = {
#    'email':r'wudizhangzhi@163.com',
#    'password':'zzc549527',
#    '_xsrf':_xsrf,
#    'remember_me':'true'
#        }
#
# r = s.post(url_login, data=data, verify=False)
# print(r.status_code)
# if r.json()['r'] == '0':
#    print r.json()['msg']
# print(r.content)

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

# 一些设置
url_login_get = 'https://www.zhihu.com/#signin'
url_login_post = 'https://www.zhihu.com/login/email'
email = 'wudizhangzhi@163.com'
password = 'zzc549527'
verify = False
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


class ZhiHu():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(header)
        self._login = False
        pass

    def get(self, url):
        return self.session.get(url, verify=verify)

    def login(self):
        r = self.session.get(url_login_get, verify=verify)
        _xsrf = re.findall('xsrf(.*)', r.text)[0][8:42]
        data = {
            'email': email,
            'password': password,
            '_xsrf': _xsrf,
            'remember_me': 'true'
        }
        r = self.session.post(url_login_post, data=data, verify=verify)
        if r.json()['r'] == 0:
            self._login = True
            print '登录成功'
        else:
            print '登录失败：%s', r.json()

    def _num_watched(self, html):
        pass

    def _num_followed(self, html):
        # TODO
        soup = BeautifulSoup(html)
        return soup.find_all('div', class_='zg-gray-normal')

    def _question_sign(self, soup):
        # 关注人数,浏览人数，回答数
        l = soup.find_all('div', class_='zg-gray-normal')
        follow = l[0].find_all('strong')[0].get_text()
        watch = l[2].find_all('strong')[0].get_text()
        return follow, watch

    def _question_unsign(self, soup):
        # 未登录时只能看到关注人数
        # 关注人数
        text = soup.find('div', class_='zm-side-section-inner zg-gray-normal').get_text()
        m = re.search(r'([0-9]+)', text)
        if m:
            follow = m.group()
        return follow

    def question(self, url):
        question_id = re.search(r'\d+', url).group()
        r = self.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        import chardet
        
        # 题目
        title = soup.find('h2', class_='zm-item-title').get_text()
        # chardet.detect(title)
        # 描述
        content = soup.find('div', id='zh-question-detail').get_text()
        # 回答数量
        num_answer = soup.find('h3', id='zh-question-answer-num').attrs['data-num']

        follow = ''
        watch = ''
        t = int(time.time())
        # TODO 保存数据
        if self._login:
            follow, watch = self._question_sign(soup)
            sql = 'insert into zhihu_question(question_id, title, content, time, num_answer, num_follow, num_watch) '\
            'values(%s, %s, %s, %s, %s, %s, %s)'
            db.execute(sql, question_id, title, content, t, num_answer, follow, watch)
        else:
            follow = self._question_unsign(soup)
            sql = 'insert into zhihu_question(question_id, title, content, time, num_answer, num_follow) '\
            'values(%s, %s, %s, %s, %s, %s)'
            db.execute(sql, question_id, title, content, t, num_answer, follow)

    def answer(self, soup, question_id):
        r = soup.find('div', id='zh-question-answer-wrap')
        items = r.find_all('div', class_='zm-item-answer')
        params= []
        for answer in items:
            p = []
            agree = answer.find('span', class_='count').get_text()
            token = int(answer.get('data-atoken'))
            print token
            try:
                username = answer.find('a', class_='author-link').get_text()
            except:
                username = '匿名用户'
            # user_info = answer.find('span', class_='bio').get_text()
            # summary = answer.find('div', class_='zh-summary').get_text()

            content = answer.find('div', class_='zm-editable-content')
            
            num_comment = answer.find('a', class_='toggle-comment').get_text()
            num_comment = re.search(r'\d+', num_comment).group()

            time_edit = answer.find('a', class_='answer-date-link').get_text()
            # 判断是日期还是时间
            if '-' not in time_edit:
                time_num = time_edit[-5:]
                date_today = time.strftime('%Y-%m-%d', time.localtime())
                time_num = date_today + ' ' + time_num
                time_num = int(time.mktime(time.strptime(time_num, '%Y-%m-%d %H:%M')))
                if '昨天' in time_edit:
                     time_num = time_num - 24*60*60                       
            else:# 日期
                time_num = int(time.mktime(time.strptime(time_edit[-10:], '%Y-%m-%d')))
            # TODO 保存数据
            p = [question_id, username, agree, content, num_comment, time_num]
            params.append(p)
        # sql = 'insert into zhihu_answer(question_id,username,agree,content,num_comment,time) values(%s,%s,%s,%s,%s,%s)'
        # db.executemany(sql, params)

    def _user(self, soup):
        # 登录 or 未登录
        part = soup.find('div', class_='ellipsis')
        name = part.find('span', class_='name').get_text()
        sign = part.find('span', class_='bio').get_text()

        avatar = soup.find('img', class_='Avatar').get('src')

        gender = soup.find('span', class_='gender').find('i').get('class')[1].split('-')[-1]

        education = soup.find('span', class_='education').get('title')

        agree = soup.find('span', class_='zm-profile-header-user-agree').find('strong').get_text()

        thanks = soup.find('span', class_='zm-profile-header-user-thanks').find('strong').get_text()

        num_part = soup.find('div', class_='profile-navbar').find_all('a')
        num = []
        for a in num_part:
            num.append(a.find('span').get_text())

        asks = num[1]
        answkers = num[2]
        posts = num[3]
        collections = num[4]
        logs = num[5]

        followpart = soup.find('div', class_='zm-profile-side-following').find_all('a', class_='item')
        followees = followpart[0].find('strong').get_text()
        followers = followpart[1].find('strong').get_text()

        watched = soup.find('a', class_='zg-link-litblue').get_text()
        m = re.search(r'\d+',watched)
        watched = m.group()
        #TODO 保存数据
        pass

    def user(self, url):

        r = self.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        # 登录 or 未登录
        self._user()

    def find_question_url(self, soup):
        '''

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
    zhihu = ZhiHu()
    # zhihu.login()
    r = zhihu.get('https://www.zhihu.com/question/41035200')
    soup = BeautifulSoup(r.content, 'lxml')
    zhihu.answer(soup, '41035200') 

