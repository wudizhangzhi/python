#!/usr/bin/python
# coding=utf-8

from bs4 import BeautifulSoup
import re

f = open('user.html')
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
a = soup.find_all('a')
for i in a:
    href = i.get('href')
    m = re.search(r'/question/(\d+)', str(href))
    if m:
        print m.group()[-8:]
