#!/usr/bin/python
# coding=utf8

import requests
import re
import subprocess
# r = requests.get('http://www.time.ac.cn/stime.asp', timeout=2)
# if r.status_code==200:
#     content= r.content
#     m = re.search(r'<span id="colocklocal_8e">.*</span>', content)
#     print m 
# else:
#     print r.status_code


apikey = 'b3bddbfd7081688c8c2f985e523a1d0a'

# r = requests.get('http://shijian.duoshitong.com/time.php', timeout=2)
# if r.status_code==200:
#     content= r.content
#     m = re.search(r'<span style="color:Blue">(.*)</span>', content)
#     t = m.group(1)
#     print t.decode('gbk')
# else:
#     print r.status_code


# p = subprocess.Popen("curl --get --include 'http://apis.baidu.com/3023/time/time' -H 'apikey:%s'" % apikey,
#                         stdout=subprocess.PIPE, shell=True)

# ret = p.communicate()
# beijing = ''
# if ret:
#     for info in set(re.sub(r' ', '', ret[0]).split('\n')):
#         if info:
#             if info.startswith('{'):
#                 beijing = eval(info)['stime']

# print beijing

p = subprocess.Popen("curl icanhazip.com --connect-timeout 10", stdout=subprocess.PIPE, shell=True)
ret = p.communicate()
print ret