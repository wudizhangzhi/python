#!/usr/bin/python
#coding=utf-8
import requests

def getRobots(url):
    r = requests.get(url + '/robots.txt')
    print r.content





if __name__ == '__main__':
    getRobots('http://www.baidu.com')
