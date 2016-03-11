#!/usr/bin/python3
# coding=utf-8

import torndb
import redis

mysql_host = 'localhost'
mysql_db = 'zhihu'
mysql_user = 'root'
mysql_pass = 'admin'

db = torndb.Connection(mysql_host, mysql_db, user=mysql_user, password=mysql_pass)


pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

redis_cache = redis.Redis(connection_pool=pool)

