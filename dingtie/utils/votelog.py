#/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import redis
import torndb
import json
import time

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

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)


def errorlog(handler, method, sql, msg):
    try:
        t = int(time.time())
        sql = 'insert into system_errlog(`handler`, `method`, `sql`, `msg`, `datetime`)  values(%s, %s, %s, %s, %s)'
        mysql_cursor.execute(sql, handler, method, sql, msg, int(time.time()))
    except Exception,e:
        print e


def processlog(processname, logtype, method, msg):
    try:
        t = int(time.time())
        sql = 'insert into system_processlog(`processname`, `logtype`, `msg`, `method`, `datetime`) values(%s, %s, %s, %s, %s)'
        mysql_cursor.execute(sql, processname, logtype, msg, method, t)
    except Exception,e:
        print e
