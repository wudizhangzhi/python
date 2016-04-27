#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from math import ceil
import datetime
import requests
import torndb
import redis
import json
import time
import sys
import re
from votelog import processlog

reload(sys)
sys.setdefaultencoding('utf8')

timeout = 2
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
    processlog('autovote_agent', 0, 'config', str(ex))
    sys.exit(-1)

# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


def autovote():
    # 获取commentid
    postid_commentid = redis_cursor.lpop(pre_system + 'commentidqueque')
    if not postid_commentid:
        print '%s null' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return 0

    postid = postid_commentid.split('|')[0]
    commentId = postid_commentid.split('|')[1]
    docId = postid_commentid.split('|')[2]
    shorturl = postid_commentid.split('|')[3]
    adminid = postid_commentid.split('|')[4]

    processlog('autovote_agent', 1, 'autovote', '爬取:postid:%s, commetnid:%s, drcid:%s, shorturl: %s' % (postid, commentId, docId, shorturl))

    # adminid = mysql_cursor.query('select adminid from system_url_posts where postid=%s', postid)[0]['adminid']


    # TODO 修改完成判断为截图完成
    # 搜索截图完成队列中是否含有本条帖子
    if redis_cursor.hexists(pre_system + 'complete', '%s|%s|%s|%s' % (postid, commentid, docId, shorturl)):

        return 0


    # 获取代理ip 如果没有代理ip则为127.0.0.1
    proxy_ip = redis_cursor.lpop(pre_system + 'proxylist')
    if not proxy_ip:
        proxy_ip = '127.0.0.1'

    # 判断帖子现在是否是开启状态
    ret = redis_cursor.hget(pre_system + 'commentidstatus', postid_commentid)
    if ret == '0':
        # 帖子处于停止状态
        print '%s 帖子:%s处于停止状态!' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), postid)
        processlog('autovote_agent', 1, 'autovote', '%s 帖子:%s处于停止状态!' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), postid))
        # # 将commentid写回队列
        # redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))

        # 将代理ip写入队列
        redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)
        return 0

    # 判断此代理ip是否能够访问
    ret = redis_cursor.hget(pre_system + 'ipinterval_' + postid_commentid, proxy_ip)
    if ret:
        t = int(time.mktime(datetime.datetime.now().timetuple()))
        if t <= int(ret):
            # 将代理ip写入队列
            redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)

            # 将commentid写回队列
            redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))
            return 0


    # 判断次数有没有顶贴完成
    sql = 'select `count`, `maxcount` from system_url_posts where `postid`=%s'
    ret = mysql_cursor.query(sql, postid)
    if ret:
        count_now = int(ret[0]['count'])
        count_max = int(ret[0]['maxcount'])
        if count_now >= count_max:
            # 设置状态postid状态为已完成
            sql = 'update system_url_posts set `status`=3 where `postid`=%s'
            mysql_cursor.execute(sql, postid)

            # 删除本条postid对应的hash表
            redis_cursor.delete(pre_system + 'ipinterval_' + postid_commentid)

            # 已经采集完成 删除status信息
            redis_cursor.hdel(pre_system + 'commentidstatus', postid_commentid)

            # 将代理ip写入队列
            redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)

            # 删除autovote_commentidadded 表中的记录 以免在顶贴目标完成之后  再次增加次数无法在进行添加
            redis_cursor.hdel(pre_system + 'commentidadded', postid_commentid)
            print 'Postid: %s 已经达到顶贴目标, 无需在加入队列: [%s]' % (postid, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            processlog('autovote_agent', 1, 'autovote', 'Postid: %s 已经达到顶贴目标, 无需在加入队列: [%s]' % (postid, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            # # TODO 截图
            # # 方案二：如果顶帖完成，保存到redis一个完成的列表,截图程序轮询这个列表
            # redis_cursor.lpush(pre_system + 'postidfinished', postid + "|" + shorturl)
            
            # if shorturl in 'comment.news.163.com':
            #     urltype = '163'
            # if shorturl in 'gentie.ifeng.com':
            #     urltype = 'ifeng'

            # try:
            #     sql = 'select url from system_url_post as posts, system_url_list as list where postid=%s and post.urlid=list.urlid'
            #     url_img = mysql_cursor.query(sql, postid)[0]['url']
            #     OutPutImg(url, urltype, postid)

            # except Exception,e:
            #     print '截图错误：%s' % str(e)
            return 0 
    else:
        print '没有记录 [%s]' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        processlog('autovote_agent', 1, 'reWriteScreenShotQueue', '没有记录 [%s]' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        return 0

    try:
        if shorturl in 'comment.news.163.com':
            url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/%s/action/upvote?ibc=newspc' % (
            docId, commentId)

        if shorturl in 'gentie.ifeng.com':
            url = 'http://comment.ifeng.com/vote.php?callback=recmCallback&cmtId=%s&job=up&docUrl=%s&callback=recmCallback&format=js' % (commentId, docId)

        headers = {
            'Host': '%s' % shorturl,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # 网易新闻参数
        data = {
            'ibc': 'newspc'
        }

        if proxy_ip == '127.0.0.1':
            if shorturl in 'comment.news.163.com':
                ret = requests.post(url, data=data, headers=headers, timeout=2)
            if shorturl in 'gentie.ifeng.com':
                ret = requests.get(url, headers=headers, timeout=2)
        else:
            try:
                proxies = {'http': 'http://' + proxy_ip}
                # 网易新闻
                if shorturl in 'comment.news.163.com':
                    ret = requests.post(url, data=data, proxies=proxies, headers=headers, timeout=2)
                # 凤凰新闻
                if shorturl in 'gentie.ifeng.com':
                    ret = requests.get(url, headers=headers, timeout=2)
            except requests.RequestException:
                # 判断ip发生异常的次数  超过三次则移除IP
                timeout_count = redis_cursor.hget(pre_system + 'iptimeoutcount', proxy_ip)
                print 'timeout_count: %s' % timeout_count
                if timeout_count:
                    if int(timeout_count) > 2:
                        print 'IP: %s 发生异常, 异常次数: %s  移除IP！' % (proxy_ip, int(timeout_count))
                        processlog('autovote_agent', 1, 'autovote', 'IP: %s 发生异常, 异常次数: %s  移除IP！' % (proxy_ip, int(timeout_count)))
                        # 删除autovote_ipinterval hash表
                        redis_cursor.hdel(pre_system + 'ipinterval_' + postid_commentid, proxy_ip)
                        redis_cursor.hdel(pre_system + 'iptimeoutcount', proxy_ip)
                    else:
                        print 'IP: %s 发生异常, 异常次数: %s ！' % (proxy_ip, int(timeout_count))
                        processlog('autovote_agent', 1, 'autovote', 'IP: %s 发生异常, 异常次数: %s ！' % (proxy_ip, int(timeout_count)))
                        redis_cursor.hset(pre_system + 'iptimeoutcount', proxy_ip, int(timeout_count) + 1)
                        redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)
                else:
                    print 'IP: %s 发生异常, 异常次数: %s ！' % (proxy_ip, 1)
                    processlog('autovote_agent', 1, 'autovote', 'IP: %s 发生异常, 异常次数: %s ！' % (proxy_ip, 1))
                    redis_cursor.hset(pre_system + 'iptimeoutcount', proxy_ip, 1)
                    redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)
                # 将commentid写回队列
                redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))
                return 1
        if ret.status_code == 200:
            if len(ret.text) <= 60:
                # 删除之前timeout的次数
                redis_cursor.hdel(pre_system + 'iptimeoutcount', proxy_ip)
                # 一分钟之后才能继续采集
                if shorturl in 'comment.news.163.com':
                    nxt_time = int(time.mktime(time.localtime(time.time() + int(1) * 60)))
                # 时间间隔5秒钟
                if shorturl in 'gentie.ifeng.com':
                    nxt_time = int(time.mktime(time.localtime(time.time() + int(1) * 5)))
                redis_cursor.hset(pre_system + 'ipinterval_' + postid_commentid, proxy_ip, nxt_time)
                if shorturl in 'gentie.ifeng.com':
                    if 'alert' not in ret.text:
                        sql = 'update system_url_posts set `count`=`count`+1 where `postid`=%s'
                        mysql_cursor.execute(sql, postid)
                        print '%s 成功顶贴一次! 顶贴IP: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), proxy_ip)
                        processlog('autovote_agent', 1, 'autovote', '%s 成功顶贴一次! 顶贴IP: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), proxy_ip))
                    else:
                        print '%s 凤凰新闻顶贴时间过快!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        processlog('autovote_agent', 1, 'autovote', '%s 凤凰新闻顶贴时间过快!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    # 将commentid写回队列
                    redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))
                    # 将代理ip写入队列
                    redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)
                    return 1
                if shorturl in 'comment.news.163.com':
                    sql = 'update system_url_posts set `count`=`count`+1 where `postid`=%s'
                    mysql_cursor.execute(sql, postid)

                # 写入统计表
                sql = 'insert into system_post_detail (`postTime`, `count`, `adminid`) values (%s, 1, %s)'
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                mysql_cursor.execute(sql, t, adminid)
                del t
                print '%s 成功顶贴一次! 顶贴IP: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), proxy_ip)
                processlog('autovote_agent', 1, 'autovote', '%s 成功顶贴一次! 顶贴IP: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), proxy_ip))

                # 将代理ip写入队列
                redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)
            else:
                print 'IP: %s , 返回值长度为: %s, 不是有效代理!, 从代理列表剔除!' % (proxy_ip, len(ret.text))
                processlog('autovote_agent', 1, 'autovote', 'IP: %s , 返回值长度为: %s, 不是有效代理!, 从代理列表剔除!' % (proxy_ip, len(ret.text)))
                # 删除autovote_ipinterval hash表
                redis_cursor.hdel(pre_system + 'ipinterval_' + postid_commentid, proxy_ip)
        elif ret.status_code == 429:
            # 10秒之后才能继续采集
            print '%s 顶贴太频繁！' % proxy_ip
            nxt_time = int(time.mktime(time.localtime(time.time() + int(1) * 10)))
            redis_cursor.hset(pre_system + 'ipinterval_' + postid_commentid, proxy_ip, nxt_time)
        else:
            print '顶贴失败! 状态码: %s IP: %s' % (ret.status_code, proxy_ip)
            processlog('autovote_agent', 1, 'autovote', '顶贴失败! 状态码: %s IP: %s' % (ret.status_code, proxy_ip))
            # 删除autovote_ipinterval hash表
            redis_cursor.hdel(pre_system + 'ipinterval_' + postid_commentid, proxy_ip)

        # 将commentid写回队列
        redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))
        return 1
    except Exception, ex:
        print ex
        processlog('autovote_agent', 0, 'autovote', str(ex))
        # 将代理ip写入队列
        redis_cursor.rpush(pre_system + 'proxylist', proxy_ip)

        # 将commentid写回队列
        redis_cursor.rpush(pre_system + 'commentidqueque', '%s|%s|%s|%s' % (postid, commentId, docId, shorturl))
        return 0


def main():
    while 1:
        autovote()
        print '%s sleep 1 seconds!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        time.sleep(1)


if __name__ == '__main__':
    main()
