#coding=utf-8
__author__ = 'Administrator'
import cookielib,urllib2
import socket

class HttpClient(object):
    __cookie=cookielib.CookieJar()
    __req=urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))
    __req.addheaders=[
        ('Accept', 'application/javascript, */*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')
    ]

    def Get(self,url,refer=None):
        try:
            req=urllib2.Request(url)
            if not (refer is None):
                req.add_header('Referer',refer)
            return urllib2.urlopen(url,timeout=120).read()
        except urllib2.HTTPError, e:
          return e.read()
        except socket.timeout, e:
          return ''
        except socket.error, e:
          return ''