#!/usr/bin/python

import requests
#coding=utf-8
import re
import webbrowser
import time

url_login = 'http://w.qq.com/'
url_downcode = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=%s' % (time.time()/10**10)
url_1 = 'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http://w.qq.com/proxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
url_checkcode = 'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http://w.qq.com/proxy.html?login2qq=1&webqq_type=10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-2570&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10158&login_sig=&pt_randsalt=0'



headers = {
    'Accept': 'application/javascript, */*;q=0.8',
    'Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
}


session = requests.Session()

r = session.get(url_login, headers=headers)
session.get(url_1)

webbrowser.open(url_downcode)
for i in session.cookies.items():
    print i
while True:
    r = session.get(url_checkcode, headers=headers)
    print r.text
    time.sleep(10)
