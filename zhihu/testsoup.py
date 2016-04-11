#!/usr/bin/python
# coding=utf-8

from bs4 import BeautifulSoup
import re

# f = open('question_unsign.html')
# soup = BeautifulSoup(f.read(), 'lxml')
# r = soup.find('div', id='zh-question-answer-wrap')
# item = r.find_all('div', class_='zm-item-answer')
# answer = item[0]
# agree = answer.find('span', class_='count').get_text()
# username = answer.find('a', class_='author-link').get_text()
# user_info = answer.find('span', class_='bio').get_text()
# summary = answer.find('div', class_='zh-summary').get_text()
#
# content = answer.find('div', class_='zm-editable-content')
# time_edit = answer.find('a', class_='answer-date-link').get_text()[-10:]
# num_comment = answer.find('a', class_='toggle-comment').get_text()
# num_comment = re.search(r'\d+', num_comment).group()

# 找出所有符合的url
# 例如/question/000000;/people/name
#a = soup.find_all('a')
#for i in a:
#    href = i.get('href')
#    m = re.search(r'/question/(\d+)', str(href))
#    if m:
#        print m.group()[-8:]

#用户的url
#a = soup.find_all('a')
#for i in a:
#    href = i.get('href')
#    m = re.search(r'/people/[^/]*', str(href))
#    if m:
#        print m.group().split('/')[2]

#个人信息页面
# part = soup.find('div', class_='ellipsis')
# # name = part.find('span', class_='name').get_text()
# name = part.find('a', class_='name').get_text()
# sign = part.find('span', class_='bio').get_text()

# avatar = soup.find('img', class_='Avatar').get('src')

# gender = soup.find('span', class_='gender').find('i').get('class')[1].split('-')[-1]

# education = soup.find('span', class_='education').get('title')

# agree = soup.find('span', class_='zm-profile-header-user-agree').find('strong').get_text()

# thanks = soup.find('span', class_='zm-profile-header-user-thanks').find('strong').get_text()

# num_part = soup.find('div', class_='profile-navbar').find_all('a')
# num = []
# for a in num_part:
#     num.append(a.find('span').get_text())

# asks = num[1]
# answers = num[2]
# posts = num[3]
# collections = num[4]
# logs = num[5]

# followpart = soup.find('div', class_='zm-profile-side-following').find_all('a', class_='item')
# followees = followpart[0].find('strong').get_text()
# followers = followpart[1].find('strong').get_text()

# watched = soup.find('a', class_='zg-link-litblue').get_text()
# m = re.search(r'\d+',watched)
# if m:
#     watched = m.group()



# r = soup.find('div', id='zh-question-answer-wrap')
# items = r.find_all('div', class_='zm-item-answer')
# for item in items:
#     answer_status = item.find('div', class_='answer-status')
#     print answer_status


cookie = {'www.zhihu.com': {'/': {'_xsrf': Cookie(version=0, name='_xsrf', value='348f194ee5f645a31a44b50476ddf1fa', port=None, port_specified=False, domain='www.zhihu.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False)}}, '.zhihu.com': {'/': {'q_c1': Cookie(version=0, name='q_c1', value='6e88240047ea47d19cba54da5fb9df23|1459826951000|1459826951000', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1554434951, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'z_c0': Cookie(version=0, name='z_c0', value='"QUFCQWkyMGNBQUFYQUFBQVlRSlZUUWUtS2xkVTlwUFBSRF83blo4VGxHeVl0dHpSbTdXdy13PT0=|1459826952|6c7bdc64d3589a70f785654a11eda8f5e0def26e"', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1462418951, discard=False, comment=None, comment_url=None, rest={'httponly': None}, rfc2109=False), 'unlock_ticket': Cookie(version=0, name='unlock_ticket', value='"QUFCQWkyMGNBQUFYQUFBQVlRSlZUUTg0QTFmX0ZhVlpMYVh5aTVDTm8xdmNwdUs4STJVYm9BPT0=|1459826952|e647629dacceb92d13676e354041488b1a8cd3c8"', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1459828692, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), '__ytma': Cookie(version=0, name='cap_id', value='"ODUwNjQzNjk2OGExNDVlZjk2OWE3ZDYyYjgyMGFkYTE=|1459826951|dff8c4873fb21053dac34b33911150b2c40505d7"', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1462418951, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'l_cap_id': Cookie(version=0, name='l_cap_id', value='"NDE0N2JkNWE4ZjZkNDNmNjg1NDBmMzgxNDMzM2Q1ODc=|1459826951|fa67fa6839cbd4aec1306743a6fb03559f342d3b"', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1462418951, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'login': Cookie(version=0, name='login', value='"M2UzMTk3MmU5NDc4NGEyZGEyNDUwNjZkNDAwNGIzN2Y=|1459826952|50924d6d550374d0a59ba5c13dc6bcb9fc4dfc7b"', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1462418952, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'n_c': Cookie(version=0, name='n_c', value='1', port=None, port_specified=False, domain='.zhihu.com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False)}}}
print cookie['www.zhihu.com'].keys