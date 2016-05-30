#!/usr/bin/python
#coding=utf-8

import requests
import re
import webbrowser
import time

url_login = 'http://w.qq.com/login.html'
url_downcode = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=%s' % (time.time()/10**10)
url_checkcode = 'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&'\
'u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&'\
'dumy=&fp=loginerroralert&action=0-0-2570&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10158&login_sig=&'\
'pt_randsalt=0'



headers = {
    'Accept': 'application/javascript, */*;q=0.8',
    'Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
}

session = requests.Session()

r = session.get(url_login, headers=headers)

m = re.findall(r'\.src = "(.+?)"', r.text)
if m:
    url_init = m[0]
    r = session.get(url_init)
    APPID = re.findall(r'g_appid\s*=\s*encodeURIComponent\s*\("(\d+)"', r.text)[0]
    sign = re.findall(r'g_login_sig\s*=\s*encodeURIComponent\s*\("(.*?)"\)', r.text)[0]
    JsVer = re.findall(r'g_pt_version\s*=\s*encodeURIComponent\s*\("(\d+)"\)', r.text)[0]
    MiBaoCss = re.findall(r'g_mibao_css\s*=\s*encodeURIComponent\s*\("(.+?)"\)', r.text)[0]
    print APPID
    print sign
    print JsVer
    print MiBaoCss


    # webbrowser.open(url_downcode)
    # for i in session.cookies.items():
    #     print i
    #
    # time.sleep(5)
    # r = session.get(url_checkcode, headers=headers)
    # print r.text
