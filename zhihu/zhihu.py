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
from conndb import *

# mysql_host = 'localhost'
# mysql_db = 'zhihu'
# mysql_user = 'root'
# mysql_pass = 'admin'

# db = torndb.Connection(mysql_host, mysql_db, user=mysql_user, password=mysql_pass)
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
#    'email':r'',
#    'password':'',
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
email = ''
password = ''
verify = False
header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.8',
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

    def question(self, question_id):
        # question_id = re.search(r'\d+', url).group()
        try:
            url = 'https://www.zhihu.com/question/%s' % question_id
            r = self.get(url)
            soup = BeautifulSoup(r.content, 'lxml')

            # 题目
            title = soup.find('h2', class_='zm-item-title').get_text()
            # chardet.detect(title)
            # 描述
            content = soup.find('div', id='zh-question-detail').get_text()
            # 回答数量
            num_answer = soup.find('h3', id='zh-question-answer-num')
            if num_answer:
                num_answer = num_answer.attrs['data-num']
            else:
                num_answer = 0

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
                try:
                    sql = 'insert into zhihu_question(`question_id`, `title`, `content`, `time`, `num_answer`, `num_follow`) values(%s, %s, %s, %s, %s, %s)'
                    db.execute(sql, question_id, title, content, t, num_answer, follow)
                except Exception,e:
                    print e
                    print 'error: insert into zhihu_question(question_id, title, content, time, num_answer, num_follow) values(%s, %s, %s, %s, %s, %s)' % (question_id, title, content, t, num_answer, follow)

            # 采集答案
            # self.answer(soup, question_id)
        except Exception,e:
            print '问题地址:%s;error:%s' % (question_id,str(e))



    def answer(self, soup, question_id):
        r = soup.find('div', id='zh-question-answer-wrap')
        items = r.find_all('div', class_='zm-item-answer')
        params= []
        for answer in items:
            p = []
            answer_status = answer.find('div', class_='answer-status')
            if answer_status:
                continue
            agree = answer.find('span', class_='count').get_text()
            token = int(answer.get('data-atoken'))
            try:
                username = answer.find('a', class_='author-link').get_text()
            except:
                username = '匿名用户'
            # user_info = answer.find('span', class_='bio').get_text()
            # summary = answer.find('div', class_='zh-summary').get_text()

            content = answer.find('div', class_='zm-editable-content')

            try:
                num_comment = answer.find('a', class_='toggle-comment').get_text()
            except:
                continue
                break
            m = re.search(r'\d+', num_comment)
            if m:
                num_comment = m.group()
            else:
                num_comment = 0


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
            p = [question_id, token, username, content, time_num]
            params.append(p)
        sql = 'insert into zhihu_answer(question_id,token,username,content,time) values(%s,%s,%s,%s,%s)'
        db.executemany(sql, params)

    def _user(self, soup, urlname):
        '''
        用户信息
        '''

        # 登录 or 未登录
        part = soup.find('div', class_='ellipsis')
        name = part.find('span', class_='name').get_text()
        # about界面下
        # name = part.find('a', class_='name').get_text()
        sign = part.find('span', class_='bio')
        if sign:
            sign = sign.get_text()
        else:
            sign = ''


        # 用户数据
        # self._user_data(soup, urlname)

        avatar = soup.find('img', class_='Avatar').get('src')

        gender = soup.find('span', class_='gender')
        if gender:
            gender = gender.find('i').get('class')[1].split('-')[-1]
            if gender == 'female':
                gender = 0
            else:
                gender = 1
        else:
            gender = 2
        # education = soup.find('span', class_='education').get('title')


        # params = [name,sign,avatar,gender]
        # for i in params:
        #     print str(i)
        try:
            #保存数据
            sql = 'insert into zhihu_user(name,urlname,sign,avatar,gender) values(%s,%s,%s,%s,%s)'
            db.execute(sql, name, urlname, sign, avatar, gender)
        except Exception,e:
            print '用户地址:%s ;error:%s' % (urlname, str(e))


    def _user_data(self, soup, urlname):
        '''
        用户数据
        '''
        agree = soup.find('span', class_='zm-profile-header-user-agree').find('strong').get_text()

        thanks = soup.find('span', class_='zm-profile-header-user-thanks').find('strong').get_text()

        num_part = soup.find('div', class_='profile-navbar').find_all('a')
        num = []
        for a in num_part:
            num.append(a.find('span').get_text())

        asks = num[1]
        answers = num[2]
        posts = num[3]
        collections = num[4]
        logs = num[5]

        followpart = soup.find('div', class_='zm-profile-side-following').find_all('a', class_='item')
        followees = followpart[0].find('strong').get_text()
        followers = followpart[1].find('strong').get_text()

        watched = soup.find('a', class_='zg-link-litblue').get_text()
        m = re.search(r'\d+',watched)
        watched = m.group()

        params = [urlname, agree, thanks, asks, answers, posts, collections, logs, followees, followers, watched]
        # for i in params:
        #     print i
        sql = 'insert into zhihu_user_data(urlname,agree,thanks,asks,answers,posts,collections,logs,followees,followers,watched) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        db.execute(sql, *params)

    def user(self, urlname):
        try:
            #判断是否采集过
            sql = 'select * from zhihu_user where urlname=%s'
            ret = db.query(sql, urlname)
            if not ret:
                url = 'https://www.zhihu.com/people/%s' % urlname
                # print '用户地址:%s' % url
                r = self.get(url)
                if r.status_code==200:
                    # print '采集用户:%s ;status_code:%s' % (urlname, r.status_code)
                    soup = BeautifulSoup(r.content, 'lxml')
                    # 登录 or 未登录
                    self._user(soup, urlname)
                else:
                    print '采集用户:%s ;status_code:%s' % (urlname, r.status_code)
            else:
                print '已经采集过:%s' % urlname
        except Exception,e:
            print e

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



    def follow_question(self, soup, question_id):
        '''
        关注问题
        https://www.zhihu.com/node/QuestionFollowBaseV2
        {'method':'follow_question',
         'params':"{'question_id':'8870875'}",
         '_xsrf':''
         }
        '''
        #检查是否登录
        #通过soup找到按钮的data-id，然后post

        xsrf = soup.find('input',{'name':'_xsrf'}).get('value')
        self.touch(xsrf, question_id)
        data = {
                'method':'follow_question',
                'params':'{"question_id":"%s"}' % question_id,
                '_xsrf':xsrf
                }

        r = self.session.post('https://www.zhihu.com/node/QuestionFollowBaseV2', data=data, verify=verify)
        print r
        print r.json()


    def touch(self, _xsrf, question_id):
        data = {
            'items':"[['question',%s,'read']]" % question_id,
            '_xsrf':_xsrf
        }
        r = self.session.post('https://www.zhihu.com/lastread/touch')
        print 'touch:%s' % str(r)

'''
https://zhihu-web-analytics.zhihu.com/collect
{"v":1,"cid":"17cfc08a-d1f0-4131-94b9-01d8a12cd687","uid":"31256813240320","t":"event","ni":false,"dp":"/question/25311180","ts":"1459826455399","sr":"1920x1080","vp":"1518x488","ul":"en-US","ua":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0","dl":"https://www.zhihu.com/question/25311180","dr":"https://www.zhihu.com/","de":"UTF-8","dt":"(18 条消息) 博士生们都在干什么？ - 知乎","sd":24,"ea":"click_follow_question","ec":"question_answer","el":"question_follow_question"}
'''


def user_scapy():
    '''
    用户信息采集
    '''
    client = ZhiHu()
    client.login()
    while True:
        ret = redis_cache.spop('zhihu_url_people')
        if ret:
            client.user(ret)
            print '采集用户:%s' % ret
        time.sleep(1)


if __name__ == '__main__':
    user_scapy()
    # zhihu = ZhiHu()
    # zhihu.login()
    # r = zhihu.get('https://www.zhihu.com/question/42057335')
    #
    # #_xsrf = re.findall('xsrf(.*)',r.text)[0][8:42]
    # soup = BeautifulSoup(r.content, 'lxml')
    # zhihu.follow_question(soup, 42057335 )
#     zhihu.follow_question(soup, 41658681)
#     print zhihu.session.cookies['cap_id']
#     print zhihu.session.cookies['__utmc']
    #print zhihu.find_people_url(soup)
    # zhihu.user('lu-pu-tao-21')
    # zhihu.question()
