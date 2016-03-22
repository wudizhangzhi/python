#!/usr/bin/python
#coding=utf8
'''
界面显示的设置
'''
# 主界面
version = '\033[34mLinux&&Unix日志取证大师V1.0\033[0m'

selection = ['全部日志获取','自定义选择日志']


line_help = 'q--返回上一页,退出 空格--选择 k--向下 j--向上'

# '\033[42m' +  + '\033[0m'
# 自定义选择界面

# 显示的行数
line_show = 15

log_list = ['nginx', 'httpd', 'mysqld','mongodb', 'redis','website','sys']

line_help_logview = 'q--返回上一页,退出  o--输出日志  空格--进入  m--标记  k--向下  j--向上'
# 标记样式
tab = '\033[36m✔ \033[0m'