#/usr/bin/python
# -*- coding: utf-8 -*-
import torndb
import requests
import urllib2
import redis
import time
import sys
import json
import re
from genreport import OutPutImg
import math


timeout = 3
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
    sys.exit(-1)


# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


def scrapy_hot_comments_news_163_com(docId, url, commentid, postid, siteid):
    '''
    

    '''
    print '爬取%s,%s,%s,%s,%s' % (docId, url, commentid, postid, siteid)
    # for page in range(1, 5):
    #     print '第%s页' % page
        # post参数，起始位置
    offset = 0*30
    page = 1
    inhot = False
    headers = {
        'Host': 'comment.news.163.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    # userlist = getuserlist(siteid)
    try:
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/hotTopList?offset=%s&limit=40&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc' % (docId, offset)
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = re.findall('getData\(\n(.*)\);', html, re.S | re.M)
        if ret:
            post = json.loads(ret[0])
            indexs = post['commentIds']
            for commid in indexs:
                if str(commentid) in commid:
                    # 获取热门帖子索引 k
                    index = indexs.index(commid)
                    page = math.ceil((index + 1)/10.0)
                    inhot = True
            if not inhot:
                print '热门帖中无法找到, 重新写入队列: %s' % url
                # redis重新写入截图队列
                redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))
                return

            comments = post['comments']
            for k, v in comments.items():
                commentId = v['commentId']
                if int(commentId) == int(commentid):
                    # 截图
                    res = OutPutImg(url, '163', postid, page)
                    if not res:
                        # redis重新写入截图队列
                        print '重新写入队列: %s' % url
                        redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))
                        return
                    print '截图完成: %s !' % url
        del ret
    except Exception, ex:
        print ex
        print '重新写入队列: %s' % url
        # redis重新写入截图队列
        redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))


def scrapy_hot_comments_ifeng_com(docUrl, url, commentid, postid, siteid):
    print '爬取%s,%s,%s,%s,%s' % (docUrl, url, commentid, postid, siteid)
    headers = {
        'Host': 'comment.ifeng.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    # userlist = getuserlist(siteid)
    try:
        comment_url = 'http://comment.ifeng.com/get.php?callback=hotCommentListCallBack&orderby=uptimes&docUrl=%s&format=json&job=1&p=1&pageSize=10&callback=hotCommentListCallBack&skey=16a2fe' % docUrl
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = json.loads(html)
        if ret:
            comments = ret['comments']
            for comment in comments:
                commentId = comment['comment_id']
                # commentId = comment['article_id']
                # createTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment['create_time'])))
                # userId = comment['user_id']
                # content = comment['comment_contents']
                # nickname = comment['uname']
                if commentId == commentid:
                    # 截图
                    res = OutPutImg(url, 'ifeng', postid)
                    if not res:
                        # redis重新写入截图队列
                        redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))
                    return
            print '重新写入队列: %s' % url
            # redis重新写入截图队列
            redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))
        del ret
    except Exception, ex:
        print ex
        print '重新写入队列: %s' % url
        # redis重新写入截图队列
        redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (postid, url, siteid))


def auto_screenshot():
    print '图片轮训开始'
    while True:
        screenshot = redis_cursor.rpop(pre_system + 'screenshotqueue')
        if screenshot:
            postid, url, siteid = screenshot.split('|') 
            sql = 'select * from system_url_posts where postid=%s'
            ret = mysql_cursor.query(sql, postid)
            if ret:# 爬取
                commentid = ret[0]['commentIds']

                if siteid in ['1',]:# 163
                    docId = re.findall('(.*?).html', url.split('/')[-1])[0]
                    scrapy_hot_comments_news_163_com(docId, url, commentid, postid, siteid)
                    print '%s sleep 2 mins!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    time.sleep(2*60)
                    continue
                if siteid in ['2',]:# ifeng
                    docUrl = urllib2.unquote(re.findall(r'docUrl=(.*?.shtml)', url)[0])
                    scrapy_hot_comments_ifeng_com(docUrl, url, commentid, postid, siteid)
                    print '%s sleep 2 mins!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    time.sleep(2*60)
                    continue
                if siteid in ['3',]:
                    print '%s sleep 2 mins!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    time.sleep(2*60)
                    continue
                
            else:# 写回队列
                print '%s 不在post列表中' % url
                # redis_cursor.rpush(pre_system + 'screenshotqueue', '%s|%s|%s' % (urlid, url, shorturl))
        print '%s sleep 2 mins!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        time.sleep(2*60)


if __name__ == '__main__':
    auto_screenshot()