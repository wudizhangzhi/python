#!/usr/bin/python
#coding=utf8

import tornado.web
import torndb
import redis
import json
import sys
import os

'''
接口：
    取数据;传递：分布名称，请求个数

1.autovote_agent顶帖

    postid, commentIds, docId, shorturl, adminid
    停止：1.时间
          2.是否超时

2.autoscreenshot截图

    postid, commentIds，docId, shorturl, t, t
    需要接口：1.判断是否需要截图
          2.截图完成，发送图片给主机
                删除顶帖队列

3.auto_scapyuser爬取个人页面
    
    url, siteid, t, adminid 

    需要接口：1.获取队列
          2.判断帐号是否存在
          3.帐号不存在，插入帐号
          4.判断回帖是否保存过
          5.回帖没保存过保存
          6.判断url是否添加过
          7.没添加过添加url
'''


reload(sys)
sys.setdefaultencoding('utf8')

try:
    fp = file('config/config.ini')
    config_data = fp.read()
    fp.close()

    config_json = json.loads(config_data)['config']

    redis_host = config_json['redis_host']
    redis_port = config_json['redis_port']
    mysql_host = config_json['mysql_host']
    mysql_db = config_json['mysql_db']
    mysql_user = config_json['mysql_user']
    mysql_pass = config_json['mysql_pass']

    pre_system = config_json['pre_system']
    serverport = config_json['http_port']
except Exception, ex:
    print ex
    errorlog('main', '', '', str(ex))
    sys.exit(-1)



# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


# code = mysql_cursor.query('select code from system_robot_scure')[0]['code']

class BaseInterface(tornado.web.RequestHandler):
    pass


def checkUser(obj):
    code = obj.get_argument('code', '')
    if code:
        if code != code:
            self.write('-1')
            return
    else:
        self.write('0')


class IsScreenshotInterface(BaseInterface):
    def get(self):
        '''
        判断帖子是否已经截图
        '''
        postid = self.get_argument('postid')
        sql = 'select screenshot from system_url_posts where postid=%s'
        ret = mysql_cursor.query(sql, postid)
        if ret:
            self.write('1')
        else:
            self.write('0')


class GetAgentAndScreenShotInterface(BaseInterface):
    def get(self):
        '''
        获取截图和顶帖队列
        '''
        robot = self.get_argument('robot', '')
        count = self.get_argument('count', '')
        if robot and count and int(count) < 50:
            result = []
            for i in xrange(int(count)):
                ret = redis_cursor.rpop(pre_system + robot)
                result.append(result)

            self.write(json.dumps(result))
        else:
            self.write('0')


class ScreenShotUpLoadInterface(BaseInterface):
    '''
    截图完成，发送图片给主机
    '''
    def get(self):
        postid = self.get_argument('postid', '')
        img = self.get_argument('img', '')
        f = open('%s.jpg' % postid, 'wb')
        import base64
        f.write(base64.b64decode(img))
        self.write('1')

interface = [
    (r'/isscreenshot', IsScreenshotInterface),
    (r'/getagentandscreenshot', GetAgentAndScreenShotInterface),
    (r'/screenshotupload', ScreenShotUpLoadInterface),
]


if __name__=='__main__':
    pass