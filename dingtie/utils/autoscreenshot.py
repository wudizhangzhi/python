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
from binascii import crc32
import math
from votelog import processlog


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
    processlog('autoscreenshot', 0, 'config', str(ex))
    sys.exit(-1)


# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


def reWriteScreenShotQueue(postid, docid, shorturl, commentid, crttime):
    '''
    判断alue是否超时，不超时写回队列
    '''
    try:
        if time.time() - int(crttime) < 86400:
            print '未超时, 重新写入队列: postid:%s' % postid
            # processlog('autoscreenshot', 1, 'reWriteScreenShotQueue', '未超时,重新写入队列: postid:%s' % postid)
            # redis重新写入截图队列
            redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s|%s|%s|%s' % (postid, docid, shorturl, commentid, crttime, int(time.time())))
        else:
            print '超时,%s：%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(crttime))), postid)
            processlog('autoscreenshot', 1, 'reWriteScreenShotQueue', '超时,%s：postid: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(crttime))), postid))
    except Exception,e:
        processlog('autoscreenshot', 0, 'reWriteScreenShotQueue', str(e))




def scrapy_hot_comments_news_163_com(docId, commentid, postid, shorturl, crttime):
    '''


    '''
    print '爬取%s,%s,%s,%s' % (docId, commentid, postid, shorturl)
    processlog('autoscreenshot', 1, 'scrapy_hot_comments_news_163_com', '爬取docId:%s,commentid:%s, postid:%s, %s' % (docId, commentid, postid, shorturl))
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

    try:
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/hotTopList?offset=0&limit=40&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc' % docId
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
                    # 保存楼层信息到mysql
                    sql = 'update system_url_posts set floor=%s where postid=%s'
                    mysql_cursor.execute(sql, index+1, postid)
                    inhot = True

            if not inhot:
                print '热门帖中无法找到: %s' % postid
                processlog('autoscreenshot', 1, 'scrapy_hot_comments_news_163_com', '热门帖中无法找到: %s' % postid)
                reWriteScreenShotQueue(postid, docId, shorturl, commentid, crttime)
                return

            comments = post['comments']
            for k, v in comments.items():
                commentId = v['commentId']
                if int(commentId) == int(commentid):
                    # 截图
                    res = OutPutImg(postid, '163', postid, page)
                    if not res:
                        print '截图失败'
                        processlog('autoscreenshot', 1, 'scrapy_hot_comments_news_163_com', '截图False')
                        reWriteScreenShotQueue(postid, docId, shorturl, commentid, crttime)
                        return
                    print '截图完成: %s !' % postid
                    processlog('autoscreenshot', 1, 'scrapy_hot_comments_news_163_com', '截图完成: %s ' % postid)
                # print 'commentid找不到匹配'
                # processlog('autoscreenshot', 1, 'scrapy_hot_comments_news_163_com', 'commentid找不到匹配: %s ' % commentid)
        del ret
    except Exception, ex:
        print ex
        processlog('autoscreenshot', 0, 'scrapy_hot_comments_news_163_com', str(ex))
        reWriteScreenShotQueue(postid, docId, shorturl, commentid, crttime)


def scrapy_hot_comments_ifeng_com(docUrl, commentid, postid, shorturl, crttime):

    print '爬取%s,%s,%s,%s' % (docUrl, commentid, postid, shorturl)
    processlog('autoscreenshot', 1, 'scrapy_hot_comments_ifeng_com', 'docUrl:%s,commentid:%s, postid:%s, %s' % (docUrl, commentid, postid, shorturl))

    headers = {
        'Host': 'comment.ifeng.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    try:
        comment_url = 'http://comment.ifeng.com/get.php?callback=hotCommentListCallBack&orderby=uptimes&docUrl=%s&format=json&job=1&p=1&pageSize=10&callback=hotCommentListCallBack&skey=16a2fe' % docUrl
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = json.loads(html)
        if ret:
            comments = ret['comments']
            for comment in comments:
                commentId = comment['comment_id']

                if commentId == commentid:
                    index = comments.index(comment)
                    # 保存楼层信息到mysql
                    sql = 'update system_url_posts set floor=%s where postid=%s'
                    mysql_cursor.execute(sql, index+1, postid)

                    # 截图
                    res = OutPutImg(postid, 'ifeng', postid)
                    if res:
                        # 加入截图完成队列
                        # redis_cursor.hset(pre_system + 'complete', '%s|%s|%s|%s' % (postid, commentid, docid, shorturl), 1)
                        # 更改远端帖子状态, 送图片
                        
                        pass
                    else:
                        processlog('autoscreenshot', 1, 'scrapy_hot_comments_ifeng_com', '截图False')
                        reWriteScreenShotQueue(postid, docUrl, shorturl, commentid, crttime)
                    return
            # print 'commentid找不到匹配'
            # processlog('autoscreenshot', 1, 'scrapy_hot_comments_ifeng_com', 'commentid找不到匹配: %s ' % commentid)
            reWriteScreenShotQueue(postid, docUrl, shorturl, commentid, crttime)
        del ret
    except Exception, ex:
        print ex
        processlog('autoscreenshot', 0, 'scrapy_hot_comments_ifeng_com', str(ex))
        reWriteScreenShotQueue(postid, docUrl, shorturl, commentid, crttime)


def auto_screenshot():
    print '图片轮训开始'
    processlog('autoscreenshot', 1, 'auto_screenshot', '图片轮训开始')
    while True:
        screenshot = redis_cursor.rpop(pre_system + 'screenshotqueue')
        if screenshot:
            try:
                postid, docid, shorturl,commentid, crttime, lasttime = screenshot.split('|')

                # 判断时间间隔是否太快, 不得少于2min
                if int(time.time()) - int(lasttime) < 60:
                    print 'url采集间隔过快,重新写入队列  postid:%s  ; lasttime:%s'  % (postid, lasttime)
                    # reWriteScreenShotQueue(postid, docid, shorturl, commentid, crttime)
                    redis_cursor.lpush(pre_system + 'screenshotqueue', '%s|%s|%s|%s|%s|%s' % (postid, docid, shorturl, commentid, crttime, lasttime))
                    print '%s sleep 5 sec!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    time.sleep(5)
                    continue
                # 网易新闻
                if shorturl in 'comment.news.163.com':
                    scrapy_hot_comments_news_163_com(docid, commentid, postid, shorturl, crttime)
                # 凤凰新闻
                if shorturl in 'gentie.ifeng.com':
                    scrapy_hot_comments_ifeng_com(docid, commentid, postid, shorturl, crttime)
            except Exception,e:
                print e
                processlog('autoscreenshot', 0, 'auto_screenshot', str(e))
        print '%s sleep 5 sec!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        time.sleep(5)




if __name__ == '__main__':
    auto_screenshot()
