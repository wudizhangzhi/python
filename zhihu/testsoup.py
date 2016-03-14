#!/usr/bin/python
# coding=utf-8

from bs4 import BeautifulSoup
import re

f = open('question_unsign.html')
soup = BeautifulSoup(f.read(), 'lxml')
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



r = soup.find('div', id='zh-question-answer-wrap')
items = r.find_all('div', class_='zm-item-answer')
for item in items:
    answer_status = item.find('div', class_='answer-status')
    print answer_status
