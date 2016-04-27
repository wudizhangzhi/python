#!/usr/bin/python
#coding=utf8


def pushRediss(data):
    '''
    向多个redis队列中添加顶帖的队列
    '''
    # 列出所有的分布代理
    sql = 'select * from system_distributed'
    ret = mysql_cursor.query(sql)
    for q in ret:
        redis_cursor.lpush(pre_system + q['name'], data)
        pass
    pass

