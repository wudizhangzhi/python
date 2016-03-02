#!/usr/bin/python
#coding=utf8
user={'2016-01-01':['2','/top/'],'2016-01-02':['1','/sp/'],'2016-01-01':['1','/top/'],'2016-01-01':['1','/top/'],}

tmp = []
id_list = []

for users in user:
    for ids in user[users]:
        tmp.append(ids)
    if id_list:
        id_list = list(set(id_list) & set(tmp))
    else:
        id_list = tmp
    tmp = []
print id_list
