#!/usr/bin/python
#coding=utf8

from people_thread import People
from question_thread import Question
from url_thread import Url
from threading import Thread


if __name__ == '__main__':
    people = People()
    question = Question()
    url = Url()
    start_url = 'https://www.zhihu.com/explore'
    Thread(target=url.run, args=(start_url,)).start()
    Thread(target=question.run).start()
    Thread(target=people.run).start()

'''TODO 待实现功能
1.自动关注含有关键字的问题
2.问题的关注度（关注人数上升速度，关注总数等）
'''



