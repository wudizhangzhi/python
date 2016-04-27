#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil
import requests
import urllib2
import torndb
import redis
import json
import time
import sys
import re
from votelog import processlog

reload(sys)
sys.setdefaultencoding('utf8')

timeout = 3
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
    processlog('autovote_main', 0, 'config', str(ex))
    sys.exit(-1)

# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


def getuserlist(siteid):
    # 获取内部帐号列表
    userlist = []
    sql = 'select username from system_site_user where `siteid`=%s'
    ret = mysql_cursor.query(sql, siteid)
    if ret:
        for user in ret:
            userlist.append(user['username'])
    return userlist


def seturlstatus(urlid, adminid):
    # 设置url的状态
    sql = 'update system_url_list set `status`=1 where `urlid`=%s and `adminid`=%s'
    mysql_cursor.execute(sql, urlid, adminid)
    processlog('autovote_main', 1, 'seturlstatus', '设置url的状态,urlid:%s' % urlid)


def get_comment_news_163_com_pagenum(docId, urlid):
    comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/newList?offset=0&limit=1&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc' % docId
    headers = {
        'Host': 'comment.news.163.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    try:
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        if req.status_code != 200:
            return '0'
        html = req.text
        ret = re.findall('getData\(\n(.*)\);', html, re.S | re.M)
        if ret:
            post = json.loads(ret[0])
            newListSize = int(ceil(int(post['newListSize'])/30.0))
            comments = post['commentIds']
            if comments:
                if len(comments[0].split(',')) > 1:
                    createTime = post['comments'][comments[0].split(',')[-1]]['createTime']
                else:
                    createTime = post['comments'][comments[0]]['createTime']
                if newListSize > 2:
                    num = 2
                else:
                    num = newListSize

                return json.dumps({'createTime': createTime, 'num': num})
        return json.dumps({'createTime': 0, 'num': 0})
    except Exception, ex:
        # 设置为更新状态, 这样用户可以根据实际情况进行再次采集
        seturlstatus(urlid, adminid)
        print ex
        processlog('autovote_main', 0, 'get_comment_news_163_com_pagenum', str(ex))
        return 'error'


def scrapy_comment_news_163_com(docId, urlid, lastcreateTime, siteid, url, adminid):

    headers = {
        'Host': 'comment.news.163.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    for page in xrange(6):

        userlist = getuserlist(siteid)
        try:
            comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/newList?offset=%s&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc' % (docId, page*40)
            req = requests.get(comment_url, headers=headers, timeout=timeout)
            html = req.text
            ret = re.findall('getData\(\n(.*)\);', html, re.S | re.M)
            if ret:
                post = json.loads(ret[0])
                comments = post['comments']
                for k, v in comments.items():
                    commentId = v['commentId']
                    createTime = v['createTime']
                    userId = v['user']['userId']
                    content = v['content']
                    if 'nickname' in v['user']:
                        nickname = v['user']['nickname']
                    else:
                        nickname = ''
                    if nickname in userlist:
                        # 判断记录是否已经写入过
                        sql = 'select userId,createTime from system_url_posts where `userId`=%s and `createTime`=%s and `adminid`=%s'
                        r = mysql_cursor.query(sql, userId, createTime, adminid)
                        if not r:
                            # 不存在记录  写入内容
                            sql = 'insert into system_url_posts (`urlid`, `userId`, `commentIds`, `content`, ' \
                                  '`nickname`, `createTime`, `adminid`) values (%s, %s, %s, %s, %s, %s, %s)'
                            postid = mysql_cursor.execute_lastrowid(sql, urlid, userId, commentId, content, nickname, createTime, adminid)

                        del r
                    time.sleep(0.2)
            del ret
            # 修改url记录为更新状态
            seturlstatus(urlid, adminid)
        except Exception, ex:
            seturlstatus(urlid, adminid)
            print ex
            processlog('autovote_main', 0, 'scrapy_comment_news_163_com', str(ex))
            return 0


def scrapy_comment_ifeng_com(docUrl, urlid, siteid, url, adminid):
    headers = {
        'Host': 'comment.ifeng.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    userlist = getuserlist(siteid)
    try:
        comment_url = 'http://comment.ifeng.com/get.php?callback=newCommentListCallBack&orderby=&docUrl=%s&format=json&job=1&p=1&pageSize=100&callback=newCommentListCallBack' % docUrl
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = json.loads(html)
        if ret:
            comments = ret['comments']
            for comment in comments:
                commentId = comment['comment_id']
                createTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment['create_time'])))
                userId = comment['user_id']
                content = comment['comment_contents']
                nickname = comment['uname']
                if nickname in userlist:
                    # 判断记录是否已经写入过
                    sql = 'select userId,createTime from system_url_posts where `userId`=%s and `createTime`=%s and `adminid`=%s'
                    r = mysql_cursor.query(sql, userId, createTime, adminid)
                    if not r:
                        # 不存在记录  写入内容
                        sql = 'insert into system_url_posts (`urlid`, `userId`, `commentIds`, `content`, ' \
                              '`nickname`, `createTime`, `adminid`) values (%s, %s, %s, %s, %s, %s, %s)'
                        postid = mysql_cursor.execute_lastrowid(sql, urlid, userId, commentId, content, nickname, createTime, adminid)

                    del r
        del ret
        time.sleep(2)
        # 修改url记录为更新状态
        seturlstatus(urlid, adminid)
    except Exception, ex:
        seturlstatus(urlid, adminid)
        print ex
        processlog('autovote_main', 0, 'scrapy_comment_ifeng_com', str(ex))
        return 0


def scrapy_news_sina_com_cn(channel, newsid, urlid, siteid, adminid):
    headers = {
        'Host': 'comment5.news.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    userlist = getuserlist(siteid)
    try:
        comment_url = 'http://comment5.news.sina.com.cn/page/info?format=json&channel=%s&newsid=%s&group=&compress=1&ie=utf8&oe=utf8&page=1&page_size=100' % (channel, newsid)
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = json.loads(html)
        if ret:
            comments = ret['result']['cmntlist']
            for comment in comments:
                commentId = comment['mid']
                createTime = comment['time']
                userId = comment['uid']
                content = comment['content']
                r = re.findall(r'wb_screen_name=(.*?)&', comment['config'])
                if r:
                    nickname = r[0]
                else:
                    nickname = comment['nick']
                if nickname in userlist:
                    # 判断记录是否已经写入过
                    sql = 'select userId,createTime from system_url_posts where `userId`=%s and `createTime`=%s and `adminid`=%s'
                    r = mysql_cursor.query(sql, userId, createTime, adminid)
                    if not r:
                        # 不存在记录  写入内容
                        sql = 'insert into system_url_posts (`urlid`, `userId`, `commentIds`, `content`, ' \
                              '`nickname`, `createTime`, `adminid`) values (%s, %s, %s, %s, %s, %s, %s)'
                        postid = mysql_cursor.execute_lastrowid(sql, urlid, userId, commentId, content, nickname, createTime, adminid)

                    del r
        del ret
        time.sleep(1)
        # 修改url记录为更新状态
        seturlstatus(urlid, adminid)
    except Exception, ex:
        seturlstatus(urlid, adminid)
        print ex
        processlog('autovote_main', 0, 'scrapy_news_sina_com_cn', str(ex))
        return 0


def news_sina_com_cn_getNewsid(url):
    # 返回newsid channel的值

    html = requests.get(url).text
    if html:
        ret = {}
        res_channel = re.findall(r'channel: \'(.*?)\',', html)
        if res_channel:
            ret['channel'] = res_channel[0]
        else:
            return 'error'

        res_newsid = re.findall(r'newsid: \'(.*?)\',', html)
        if res_newsid:
            ret['newsid'] = res_newsid[0]
        else:
            return 'error'

        return ret
    else:
        return 'error'


def scrapy_news_qq_com(rootid, urlid, siteid, adminid):
    headers = {
        'Host': 'comment5.news.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    userlist = getuserlist(siteid)
    try:
        comment_url = 'http://coral.qq.com/article/%s/hotcomment?reqnum=10&_=%s' % (rootid, int(time.time()))
        req = requests.get(comment_url, headers=headers, timeout=timeout)
        html = req.text
        ret = json.loads(html)
        if ret:
            comments = ret['data']['commentid']
            for comment in comments:
                commentId = comment['mid']
                createTime = comment['time']
                userId = comment['uid']
                content = comment['content']
                r = re.findall(r'wb_screen_name=(.*?)&', comment['config'])
                if r:
                    nickname = r[0]
                else:
                    nickname = comment['nick']
                if nickname in userlist:
                    # 判断记录是否已经写入过
                    sql = 'select userId,createTime from system_url_posts where `userId`=%s and `createTime`=%s'
                    r = mysql_cursor.query(sql, userId, createTime)
                    if not r:
                        # 不存在记录  写入内容
                        sql = 'insert into system_url_posts (`urlid`, `userId`, `commentIds`, `content`, ' \
                              '`nickname`, `createTime`) values (%s, %s, %s, %s, %s, %s)'
                        postid = mysql_cursor.execute_lastrowid(sql, urlid, userId, commentId, content, nickname, createTime)

                    del r
        del ret
        time.sleep(1)
        # 修改url记录为更新状态
        seturlstatus(urlid, adminid)
    except Exception, ex:
        seturlstatus(urlid, adminid)
        print ex
        processlog('autovote_main', 0, 'scrapy_news_qq_com', str(ex))
        return 0





def main():
    while 1:
        urlinfo = redis_cursor.rpop(pre_system + 'urlqueque')
        # urlinfo = '3|1970-01-01 23:59:00|http://news.sina.com.cn/c/gat/2016-04-05/doc-ifxqxcnr5291732.shtml'
        if urlinfo:
            urlinfo = urlinfo.split('|')
            urlid = urlinfo[0]
            lastcreateTime = urlinfo[1]
            url = urlinfo[2]
            adminid = urlinfo[3]
            res = r'://(.*?)/'
            ret = re.findall(res, url)
            if ret:
                shorturl = ret[0]
                # 通过shorturl来获取siteid
                siteid = ''
                sql = 'select siteid from system_site_list where `shorturl`=%s'
                r = mysql_cursor.query(sql, shorturl)
                if r:
                    siteid = r[0]['siteid']
                    del r
                else:
                    print '没有siteid'
                    del r
                    time.sleep(2)
                    continue
                if shorturl in ['comment.news.163.com']:
                    docId = re.findall('(.*?).html', url.split('/')[-1])[0]
                    scrapy_comment_news_163_com(docId, urlid, lastcreateTime, siteid, url, adminid)
                    print '%s 扫描完成!' % url
                    processlog('autovote_main', 1, 'main', '%s 扫描完成!' % url)
                    time.sleep(2)
                    continue
                if shorturl in ['gentie.ifeng.com']:
                    docUrl = urllib2.unquote(re.findall(r'docUrl=(.*?.shtml)', url)[0])
                    scrapy_comment_ifeng_com(docUrl, urlid, siteid, url, adminid)
                    print '%s 扫描完成!' % url
                    processlog('autovote_main', 1, 'main', '%s 扫描完成!' % url)
                    time.sleep(2)
                    continue
                if shorturl in ['news.sina.com.cn']:
                    channel_newsid = news_sina_com_cn_getNewsid(url)
                    if channel_newsid == 'error':
                        print '%s 获取帖子url错误, url: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), url)
                        processlog('autovote_main', 1, 'main', '%s 获取帖子url错误, url: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), url))
                        time.sleep(2)
                        continue
                    channel = channel_newsid['channel']
                    newsid = channel_newsid['newsid']
                    scrapy_news_sina_com_cn(channel, newsid, urlid, siteid, adminid)
                    print '%s 扫描完成!' % url
                    processlog('autovote_main', 1, 'main', '%s 扫描完成!' % url)
                    time.sleep(2)
                    continue
                else:
                    print '网站还不支持'
                    processlog('autovote_main', 1, 'main', '网站还不支持:%s' % url)
            else:
                print 'url wrong, %s' % url
                processlog('autovote_main', 1, 'main', 'url wrong, %s' % url)
        else:
            print '^sleep 10 seconds^'

        time.sleep(10)

if __name__ == '__main__':
    main()