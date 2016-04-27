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
from binascii import crc32
from urllib import quote, unquote
import math
import base64
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
    print ex
    processlog('auto_scrapyuser', 0, 'config', str(ex))
    sys.exit(-1)


# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)

# 爬取页数
scrapy_page = 4
 #网易从个人页面获取所有帖子


'''
  流程：
  复制个人页面url
  ——>getUsername(url) 利用re.findall()筛选出usrename,放入队列username|siteid
  ——>利用接口爬去所有帖子


  siteid = self.get_argument('siteid')
  username = self.get_argument('username')
  username = getUsername(username)
  if username:
    #插入system_site_user数据库
    sql = 'insert into system_site_user(siteid, username, createtime) values(%s,%s,now())'
    mysql_cursor.execute(sql, siteid, username)
'''

def getUsername(url):
    m = re.findall(r'username=([^\&]+)', url)
    if m:
          return m[0]
    else:
          return ''

def scrapy_comment_user_163(username, adminid, address):
    '''
    网易用户所有跟贴的爬取
    '''
    username_decode = base64.b64decode(username)
    siteid = mysql_cursor.query('select siteid from system_site_list where shorturl="comment.news.163.com"')[0]['siteid']
    # 判断用户是否存在
    sql = 'select userid,adminid from system_site_user where siteid=%s and username=%s '
    r = mysql_cursor.query(sql, int(siteid), username_decode)
    if r:
        if int(adminid) != int(r[0]['adminid']):
            print '网站帐号存在，添加人不匹配'
            processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163', '网站帐号存在，添加人不匹配,现:%s, 原:%s' % (adminid, r[0]['adminid']))
            return
        userid = r[0]['userid']
        setAddressStatus(userid, 1)
    else:
        processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163', '网站帐号不存在,添加:%s,userid:%s' % (username, adminid))

        crc32_address = crc32(address) & 0xffffffff
        sql = 'insert into system_site_user(`siteid`, `username`,`createtime`, `adminid`, `address`,  `crc32address`, `status`) values(%s, %s, now(), %s, %s, %s, 1)'
        userid = mysql_cursor.execute_lastrowid(sql, siteid, username_decode, adminid, address, crc32_address)



    headers = {
          'Host': 'comment.news.163.com',
          'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Connection': 'keep-alive'
    }
    #默认爬取6页
    for page in xrange(scrapy_page):
        url = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/users/0/comments?username=%s&offset=%s&limit=30&ibc=newspc' % (username,page)

        req = requests.get(url, headers=headers, timeout=timeout)
        if req.status_code == 200:
            data = json.loads(req.text)

            threads = data['threads']
            urllist = []

            for k,v in threads.items():
                param = {}

                _url = v['url']
                # 判断url是否支持
                res = r'://(.*?)/'
                ret = re.findall(res, _url)
                if ret:
                    shorturl = ret[0]
                    if shorturl in ['news.163.com', ]:
                        boardId = v['boardId']
                        param['docId'] = v['docId']
                        param['title'] = v['title']
                        param['url'] = 'http://comment.news.163.com/' + boardId + '/' + v['docId'] + '.html'
                        urllist.append(param)
                else:
                    processlog('auto_scrapyuser', 1, 'crapy_comment_user_163', 'url不支持:%s' % _url)


            comments = data['comments']

            for k,v  in comments.items():
                url_post = ''
                title = ''
                for u in urllist:
                    if u['docId'] == k.split('_')[0]:
                        url_post = u['url']
                        title = u['title']
                buildLevel = v['buildLevel']
                # 判断是否含有nickname, 是否是最外层的评论
                if url_post and title and v['user'].has_key('nickname') and buildLevel==1:
                    nickname = v['user']['nickname']
                    commentId = v['commentId']
                    createTime = v['createTime']
                    content = v['content'].encode('utf8')

                    #判断帖子是否保存过
                    sql = 'select postid from system_url_posts where `commentIds`=%s and createTime=%s and `adminid`=%s'
                    r = mysql_cursor.query(sql, commentId, createTime, adminid)
                    if not r:
                        #判断url是否添加过
                        crc32_url = crc32(url_post) & 0xffffffff
                        sql = 'select urlid from system_url_list where `crc32url`=%s and `adminid`=%s'
                        ret = mysql_cursor.query(sql, crc32_url, adminid)
                        if ret:#添加过
                            urlid = ret[0]['urlid']
                        else:
                            sql = 'insert into system_url_list(`siteid`, `title`, `url`, `crc32url`, `addtime`, `status`, `adminid`) values(%s,%s,%s,%s,now(),1, %s)'
                            urlid = mysql_cursor.execute_lastrowid(sql, siteid, title, url_post, crc32_url, adminid)

                            processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163','url未添加过，添加url,urlid:%s' % urlid)
                        #保存帖子
                        try:
                            sql = 'insert into system_url_posts(`urlid`, `userid`, `commentIds`, `content`, `nickname`'\
                                  ', `createTime`, `adminid`) values(%s,%s,%s,%s,%s,%s,%s)'
                            postid = mysql_cursor.execute_lastrowid(sql, urlid, userid, commentId, content, nickname, createTime, adminid)
                            print '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid)
                            processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163','保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid))

                        except Exception,e:
                            # 有的字符集无法保存
                            if 'Incorrect string value:' in str(e):
                                print '存在表情，无法保存content, nickname:%s' % nickname
                                processlog('auto_scrapyuser', 0, 'scrapy_comment_user_163', '存在表情，无法保存content, nickname:%s' % nickname)

                            elif 'Data too long for column' in str(e):
                                processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163', '帖子内容过长，重新截取写入,urlid:%s' % urlid)
                                content = content[:255]
                                sql = 'insert into system_url_posts(`urlid`, `userid`, `commentIds`, `content`, `nickname`'\
                                  ', `createTime`, `adminid`) values(%s,%s,%s,%s,%s,%s,%s)'
                                postid = mysql_cursor.execute_lastrowid(sql, urlid, userid, commentId, content, nickname, createTime, adminid)
                                print '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid)
                                processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163','保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid))

                            else:
                                print e
                                processlog('auto_scrapyuser', 0, 'scrapy_comment_user_163', str(e))
                            # 更新site_user状态
                            setAddressStatus(userid, 0)
                    else:
                        print '帖子保存过：postid:%s' % r[0]['postid']
                        # processlog('auto_scrapyuser', 1, 'scrapy_comment_user_163', '帖子保存过：postid:%s' % r[0]['postid'])

            #如果到最后一页，退出循环
            total = data['total']
            if (page + 1)*30 >= total:
                break
        else:
            print req.text
    # 更新site_user状态
    setAddressStatus(userid, 0)

def getGuidAndUsername(url):
    m = re.findall(r'guid=([^\&]+)', url)
    if m :
        guid = m[0]
    else:
        guid = ''
    m = re.findall(r'uname=([^\&]+)', url)
    if m:
        uname = m[0]
    else:
        uname = ''
    return guid, uname




def scrapy_comment_user_ifeng(guid, username, adminid, address):
    '''
    凤凰网个人页面爬取
    http://comment.ifeng.com/get? job=7 & format=json & pagesize=20 & _1460705534 & guid=65969467 & p=1
    '''
    username_decode = unquote(username)
    siteid = 2
    # 判断用户是否存在
    sql = 'select userid,adminid from system_site_user where siteid=%s and username=%s'
    r = mysql_cursor.query(sql, siteid, username_decode)
    if r:
        if int(adminid) != int(r[0]['adminid']):
            print '网站帐号存在，且adminid不符'
            processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '网站帐号存在,添加人不匹配,现:%s, 原:%s' % (adminid, r[0]['adminid']))
            return
        print '网站帐号存在'
        userid = r[0]['userid']
        setAddressStatus(userid, 1)
    else:
        processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '网站帐号不存在,添加:%s' % username)
        crc32_address = crc32(address) & 0xffffffff
        sql = 'insert into system_site_user(`siteid`, `username`,`createtime`, `adminid`, `address`, `crc32address`, `status`) values(%s, %s, now(), %s, %s, %s, 1)'
        userid = mysql_cursor.execute_lastrowid(sql, siteid, username_decode, adminid, address, crc32_address)

    headers = {
          'Host': 'comment.news.163.com',
          'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Connection': 'keep-alive'
    }
    # 默认爬取6页
    for page in xrange(scrapy_page):
        url = 'http://comment.ifeng.com/get?job=7&format=json&pagesize=20&guid=%s&p=%s' % (guid,page)

        req = requests.get(url, headers=headers, timeout=timeout)
        if req.status_code == 200:
            data = json.loads(req.text)
            comments = data['comments']
            for comment in comments:
                _url = comment['doc_url']
                # 判断url是否支持
                res = r'://(.*?)/'
                ret = re.findall(res, _url)
                if ret:
                    shorturl = ret[0]
                    if shorturl in ['news.ifeng.com',]:

                        title = comment['doc_name']#帖子标题
                        content = comment['comment_contents']

                        createTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment['create_time'])))
                        commentId = comment['comment_id']
                        nickname = comment['uname']

                        url_post = 'http://gentie.ifeng.com/view.html?docUrl=' + quote(_url.encode('utf8')) + '&docName=' + quote(title.encode('utf8'))

                        #判断帖子是否保存过
                        sql = 'select postid from system_url_posts where `commentIds`=%s and createTime=%s and `adminid`=%s'
                        r = mysql_cursor.query(sql, commentId, createTime, adminid)
                        if not r:
                            #判断url是否添加过
                            crc32_url = crc32(url_post) & 0xffffffff
                            sql = 'select urlid from system_url_list where `crc32url`=%s and adminid=%s'
                            ret = mysql_cursor.query(sql, crc32_url, adminid)

                            if ret:#添加过
                                urlid = ret[0]['urlid']
                            else:
                                sql = 'insert into system_url_list(`siteid`, `title`, `url`, `crc32url`, `addtime`,`status`, `adminid`) values(%s, %s, %s, %s, now(), 1, %s)'
                                urlid = mysql_cursor.execute_lastrowid(sql, siteid, title, url_post, crc32_url, adminid)
                                processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng','url未添加过，添加url,urlid:%s' % urlid)

                            try:
                                #保存帖子
                                sql = 'insert into system_url_posts(`urlid`, `userid`, `commentIds`, `content`, `nickname`'\
                                      ', `createTime`, `adminid`) values(%s,%s,%s,%s,%s,%s,%s)'
                                postid = mysql_cursor.execute_lastrowid(sql, urlid, userid, commentId, content, nickname, createTime, adminid)

                                print '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid)
                                processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid))
                            except Exception,e:
                                if 'Data too long for column' in str(e):
                                    processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '帖子内容过长，重新截取写入,urlid:%s' % urlid)
                                    content = content[:255]
                                    #保存帖子
                                    sql = 'insert into system_url_posts(`urlid`, `userid`, `commentIds`, `content`, `nickname`'\
                                          ', `createTime`, `adminid`) values(%s,%s,%s,%s,%s,%s,%s)'
                                    postid = mysql_cursor.execute_lastrowid(sql, urlid, userid, commentId, content, nickname, createTime, adminid)

                                    print '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid)
                                    processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '保存帖子: %s; postid :%s ; adminid : %s' % (nickname, postid, adminid))
                                # 更新site_user状态
                                setAddressStatus(userid, 0)
                        else:
                            print '帖子已经添加过: commentId:%s' % commentId
                            # processlog('auto_scrapyuser', 1, 'scrapy_comment_user_ifeng', '帖子已经添加过: commentId:%s' % commentId)

            #如果到最后一页，退出循环
            total = data['count']
            if (page + 1)*20 >= total:
                break

        else:
            print req.text
    # 更新site_user状态
    setAddressStatus(userid, 0)



def scrapy_comment_user(url, siteid, adminid):
    if siteid == '1':# 163
        username = getUsername(url)
        print 'username: %s' % username
        processlog('auto_scrapyuser', 1, 'scrapy_comment_user', 'username: %s, url:%s' % (username, url))
        if username:
            scrapy_comment_user_163(username, adminid, url)
        else:
            print '未匹配到参数'
            processlog('auto_scrapyuser', 1, 'scrapy_comment_user', '未匹配到参数, url:%s' % url)

    elif siteid == '2':# ifeng
        guid, uname = getGuidAndUsername(url)
        if guid and uname:
            print 'uname: %s' % uname
            processlog('auto_scrapyuser', 1, 'scrapy_comment_user', 'uname: %s, guid:%s, url:%s' % (uname, guid, url))
            scrapy_comment_user_ifeng(guid, uname, adminid, url)
        else:
            print '未匹配到参数'
            processlog('auto_scrapyuser', 1, 'scrapy_comment_user', '未匹配到参数, url:%s' % url)



def setAddressStatus(userid, status):
    try:
        sql = 'update system_site_user set status=%s where userid=%s'
        mysql_cursor.execute(sql,status, userid )
        print '更新状态userid:%s, status:%s' % (userid, status)
    except Exception,e:
        print e
        processlog('auto_scrapyuser', 0, 'setPageStatus', str(e))


def main():
    while True:
        ret = redis_cursor.rpop(pre_system + 'userlist')
        if ret:
            url, siteid, t, adminid = ret.split('|')

            print '爬取: %s,%s,%s,%s' % (url, siteid, t, adminid)
            processlog('auto_scrapyuser', 1, 'main', '爬取: %s, %s, %s ,adminid:%s' % (url, siteid, t, adminid))
            try:
                scrapy_comment_user(url, siteid, adminid)

            except Exception,e:
                try:
                    crc32address = crc32(url) & 0xffffffff
                    sql = 'update system_site_user set status=0 where crc32address=%s'
                    mysql_cursor.execute(sql, crc32address)
                except Exception,e:
                    processlog('auto_scrapyuser', 0, 'main', str(e))

                if 'Data too long for column' in str(e):
                    continue
                if 'Incorrect string value:' in str(e):
                    print '存在表情，无法保存content, nickname:%s' % url
                    processlog('auto_scrapyuser', 0, 'main', '存在表情，无法保存, url:%s' % url)
                    continue
                if time.time() - int(t) < 3600:
                    pass
                    # print '重新写回队列: %s' % url
                    # processlog('auto_scrapyuser', 1, 'main', '重新写回队列: %s' % url)
                    # redis_cursor.lpush(pre_system + 'userlist', '%s|%s|%s|%s' % (url, siteid, t, adminid))
                else:
                    print '超时: %s' % url
                    processlog('auto_scrapyuser', 1, 'main', '超时: %s' % url)
                print 'error: %s' % str(e)
                processlog('auto_scrapyuser', 0, 'main', str(e))
        print '%s sleep 10s!' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        time.sleep(10)


if __name__ == '__main__':
    main()
