# coding=utf-8
__author__ = 'Administrator'

import urllib2, cookielib, urllib
# ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')

class HttpClient():
    __cookie = cookielib.CookieJar()
    __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))
    __req.addheaders = [
        ('Accept', 'application/javascript, */*;q=0.8'),
        ('Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    ]
    urllib2.install_opener(__req)

    def Get(self, url, refer=None):
        try:
            req = urllib2.Request(url)
            if refer is not None:
                req.add_header('Referer', refer)
            return  urllib2.urlopen(req, timeout=120).read()

        except urllib2.HTTPError, e:
            return e.read()

    def Post(self, url, data, refer=None):
        try:
            req = urllib2.Request(url, urllib.urlencode(data))
            # req = urllib2.Request(url, data)
            if refer is not None:
                req.add_header('Referer', refer)
            s= urllib2.urlopen(req).read()
            return s
        except urllib2.HTTPError, e:
            print str(e)
            return e.read()

    def Download(self,url,file):
        print u'开始下载:url:'+url
        output=open(file,'wb')
        output.write(urllib2.urlopen(url).read())
        output.close()
        print u'下载完成：'+file

    def getCookie(self, key):
        for c in self.__cookie:
            if c.name == key:
                return c.value
        return ''

    def setCookie(self, key, val, domain):
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain, domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)

    def testcookie(self):
        return self.__cookie
