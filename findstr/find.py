#!/usr/bin/python
#coding=utf-8

'''
查找字符串的小工具

'''
import sys,os,optparse




def find(filename):
    global total
    line_num = 0
    if target == ' ':
        print '搜索内容不能为空'
        return
    if os.path.exists(filename):
        if os.path.isdir(filename):
            filelist = os.listdir(filename)
            for f in filelist:
                filepath = filename + '/' + f
                find(filepath)
        else:#是个文件
            with open(filename, 'r') as buff:
            #buff = open(filename, 'r')
                for line in buff.readlines():
                    line_num += 1
                    if target.lower() in line.lower():
                        total += 1
                        print '目标：%s 文件：%s 行号：%s' % (target, filename, line_num)

            line_num = 0

    else:
        print '路径不存在'

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='filename', help='where to find str', metavar='FILE')
    parser.add_option('-t', '--target', dest='target', help='target string')
    (options, args) = parser.parse_args()

    filename = options.filename
    target = options.target

    if not target:
        raise AssertionError('未指定搜索内容!')
    if not filename:
        raise AssertionError('未指定搜索地址!')
    total = 0
    find(filename)
    #params =  sys.argv[1:]
   # if len(params) == 2:
   #     total = 0
   #     filename = params[0]
   #     target = params[1]
   #     find(filename)

   #     print '搜索完成,共找到：%s 个结果' % total
   # else:
   #     print '参数数量不正确'
