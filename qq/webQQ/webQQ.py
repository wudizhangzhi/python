# coding=utf-8
__author__ = 'Administrator'
content=u'\u4ED6\u89E3\u6211 '
name=u"\u5B8B\u4F53"
print content.encode('utf-8')
print name.encode('utf-8')

import urllib2,cookielib
import re
from HttpClient import HttpClient

def getReValue(self, html, rex, er, ex):
    v = re.search(rex, html)
    if v is None:#如果匹配失败
      if ex:#如果条件成立,则抛异常
        raise Exception, er
      return ''
    return v.group(1)#返回匹配到的内容

smartQQUrl=r'http://w.qq.com/login.html'

httpclient=HttpClient()
#获得二维码地址
initUrl=getReValue(httpclient.Get(smartQQUrl),r'\.src = "(.+?)"', 'Get Login Url Error.', 1)
#获取二维码html
refer=r'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
html=httpclient.Get(initUrl+'0',smartQQUrl)

APPID=getReValue(html,r'g_appid=encodeURIComponent\("(\d+)"\)','Get AppId Error', 1)

sign =getReValue(html, r'g_login_sig=encodeURIComponent\("(.*?)"\)', 'Get Login Sign Error', 1)





