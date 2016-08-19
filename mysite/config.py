#!/usr/bin/python
#coding=utf-8


DEBUG = True

#数据库设置
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_db = 'mysite'
#TODO 使用其他用户并设置权限
mysql_user = 'root'
mysql_pass = 'admin'
redis_host = '127.0.0.1'
reids_port = 6379

pre_system = 'mysite_'


#
serverport = 5000
static_path = 'static'
template_path = 'templates'
cookie_secret = ''
xsrf_cookies = True
