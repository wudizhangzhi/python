#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil
import subprocess
import time
import threading
import logging


def readMemInfo():
    res = {
        'total': 0, 'free': 0, 'buffers': 0, 'cached': 0
    }
    f = open('/proc/meminfo')
    lines = f.readlines()
    f.close()
    i = 0
    for line in lines:
        if i == 4:
            break
        line = line.lstrip()
        memItem = line.lower().split()
        if memItem[0] == 'memtotal:':
            res['total'] = long(memItem[1])
            i = i + 1
            continue
        elif memItem[0] == 'memfree:':
            res['free'] = long(memItem[1])
            i = i + 1
            continue
        elif memItem[0] == 'buffers:':
            res['buffers'] = long(memItem[1])
            i = i + 1
            continue
        elif memItem[0] == 'cached:':
            res['cached'] = long(memItem[1])
            i = i + 1
            continue
    return res


def calcMemUsage():
    counters = readMemInfo()
    used = counters['total'] - counters['free'] - counters['buffers'] - counters['cached']
    total = counters['total']
    return used, total


def getlogdir(prefx, pid):
    # print '%s日志文件:' % prefx
    p = subprocess.Popen("ls -l /proc/%s/fd | grep '.log$' | awk -F '->' '{print $2}'" % pid, stdout=subprocess.PIPE,
                         shell=True)
    ret = p.communicate()
    if ret:
        logfiles = []
        for logfile in set(re.sub(r' ', '', ret[0]).split('\n')):
            if logfile:
                logfiles.append(logfile)
        return logfiles


def getDBLog(prefx, pid):
    p = subprocess.Popen(
        "ls -l /proc/%s/fd | egrep -v '/tmp/|socket:|/dev/null|/dev/urandom' | awk -F '->' '{print $2}'" % pid,
        stdout=subprocess.PIPE,
        shell=True)
    ret = p.communicate()
    if ret:
        logfiles = []
        for logfile in set(re.sub(r' ', '', ret[0]).split('\n')):
            if logfile:
                logfiles.append(logfile)
        return logfiles


def getRedisData():
    res = []
    try:
        if os.path.exists('/etc/redis/redis.conf'):
            p = subprocess.Popen("cat /etc/redis/redis.conf | grep 'dbfilename ' | awk '{print $2}'",
                                 stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            dbname = ''
            if ret:
                for name in set(re.sub(r' ', '', ret[0]).split('\n')):
                    if name:
                        dbname = name
            p = subprocess.Popen("cat /etc/redis/redis.conf | grep 'dir ' | awk '{print $2}'", stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            path = ''
            if ret:
                for p in set(re.sub(r' ', '', ret[0]).split('\n')):
                    if p:
                        path = p
            dbfilepath = ''
            if dbname and path:
                dbfilepath = path + '/' + dbname
                res.append(dbfilepath)
        elif os.path.exists('/etc/redis.conf'):
            p = subprocess.Popen("cat /etc/redis.conf | grep 'dbfilename ' | awk '{print $2}'",
                                 stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            dbname = ''
            if ret:
                for name in set(re.sub(r' ', '', ret[0]).split('\n')):
                    if name:
                        dbname = name
            p = subprocess.Popen("cat /etc/redis.conf | grep 'dir ' | awk '{print $2}'", stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            path = ''
            if ret:
                for p in set(re.sub(r' ', '', ret[0]).split('\n')):
                    if p:
                        path = p
            dbfilepath = ''
            if dbname and path:
                dbfilepath = path + '/' + dbname
                res.append(dbfilepath)
        else:
            p = subprocess.Popen("ps -C redis-server -o pid,user --no-header | head -1 | awk '{print $1}'",
                                 stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            if ret[0]:
                redis_pid = ret[0].replace('\n', '').replace('\r', '')
                p = subprocess.Popen("dirname `ls -l /proc/%s/exe | awk -F '->' '{print $2}'`" % redis_pid,
                                     stdout=subprocess.PIPE,
                                     shell=True)
                ret = p.communicate()
                path_redis = ret[0].replace('\n', '').replace('\r', '')
                path = path_redis + '/redis-cli'

                if os.path.exists(path):
                    p = subprocess.Popen("%s info server | grep 'config_file:' | awk -F ':' '{print $2}'" % path,
                                         stdout=subprocess.PIPE,
                                         shell=True)
                    ret = p.communicate()
                    path_conf = ret[0].replace('\n', '').replace('\r', '')

                    p = subprocess.Popen("cat %s | grep 'dbfilename ' | awk '{print $2}'" % path_conf,
                                         stdout=subprocess.PIPE,
                                         shell=True)
                    ret = p.communicate()
                    dbname = ret[0].replace('\n', '').replace('\r', '')
                    # if ret:
                    #     for name in set(re.sub(r' ', '', ret[0]).split('\n')):
                    #         if name:
                    #             dbname = name
                    p = subprocess.Popen("cat %s | grep 'dir ' | awk '{print $2}'" % path_conf, stdout=subprocess.PIPE,
                                         shell=True)
                    ret = p.communicate()
                    path = ret[0].replace('\n', '').replace('\r', '')
                    # if ret:
                    #     for p in set(re.sub(r' ', '', ret[0]).split('\n')):
                    #         if p:
                    #             path = p
                    dbfilepath = ''
                    if path.startswith('/'):
                        dbfilepath = path + '/' + dbname

                    else:
                        dbfilepath = path_conf.replace('redis.conf', '') + path + '/' + dbname
                        dbfilepath = dbfilepath.replace('//', '/')

                    res.append(dbfilepath)
                    # appendonly 是否开启
                    p = subprocess.Popen("cat %s | grep 'appendonly ' | awk '{print $2}'" % path_conf,
                                         stdout=subprocess.PIPE,
                                         shell=True)
                    ret = p.communicate()
                    if ret[0].replace('\n', '').replace('\r', '').lower() == 'yes':
                        p = subprocess.Popen("cat %s | grep 'appendfilename ' | awk '{print $2}'" % path_conf,
                                             stdout=subprocess.PIPE,
                                             shell=True)
                        ret = p.communicate()
                        aofname = ret[0].replace('\n', '').replace('\r', '')
                        aofpath = path_redis + '/' + aofname
                        res.append(aofpath)
                else:
                    res = ['无']  
            else:
                res = ['无'] 
    except Exception, e:
        print e
        logging.error(str(e))
        res = ['无']
    return res


def listsyslogs():
    try:
        p = subprocess.Popen("ls -l /var/log |grep ^- | awk '{print $9}'", stdout=subprocess.PIPE, shell=True)
        ret = p.communicate()
        if ret:
            logfiles = []
            for logfile in set(re.sub(r' ', '', ret[0]).split('\n')):
                if logfile:
                    logfiles.append('/var/log/%s' % logfile)
            return logfiles
    except Exception, e:
        print e
        logging.error(str(e))


def copyfile(filename, backdir):
    try:
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        targetname = backdir + dirname + '/' + basename

        # print '正在复制 %s 到 %s' % (filename, targetname)
        # typein + time
        # 判断目录是否存在
        if not os.path.exists(backdir + dirname):
            os.makedirs(backdir + dirname)
        try:
            if os.path.isdir(filename):
                logging.info(u'复制目标是文件夹：%s' % filename)
                shutil.copytree(filename, targetname)
            else:
                logging.info(u'复制目标是文件：%s' % filename)
                shutil.copy2(filename, targetname)
        except Exception, e:
            print e
            logging.error(str(e))
            # if '[Errno 13] Permission denied' in e:
            #     subprocess.Popen('sudo chmod 644 %s' % filename)
            #     shutil.copy2(filename, targetname)
    # except KeyboardInterrupt:
    except Exception, e:
        print e
        logging.error(str(e))
        print "\t\033[41m 程序终止! \033[m\n"


def copyfileByCommd(filename, backdir):
    try:
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        targetname = backdir + dirname + '/' + basename

        # print '正在复制 %s 到 %s' % (filename, targetname)
        # typein + time
        # 判断目录是否存在
        if not os.path.exists(backdir + dirname):
            os.makedirs(backdir + dirname)
        try:
            p = subprocess.Popen("cp -r %s %s" % (filename, targetname), stdout=subprocess.PIPE,
                             shell=True)
        except Exception, e:
            print e
            logging.error(str(e))
            # if '[Errno 13] Permission denied' in e:
            #     subprocess.Popen('sudo chmod 644 %s' % filename)
            #     shutil.copy2(filename, targetname)
    # except KeyboardInterrupt:
    except Exception, e:
        print e
        logging.error(str(e))
        print "\t\033[41m 程序终止! \033[m\n"


def linesnum():
    """
    测试屏幕显示行数, 每行字符数

    return: 屏幕高度 int
    屏幕宽度 int
    """
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                 '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[0]), int(cr[1])


def get_all_log():
    all_log = {}
    # nginx
    try:
        p = subprocess.Popen("ps -C nginx -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                             shell=True)
        ret = p.communicate()
        if ret[0]:
            nginx_pid = ret[0]
            ret = getlogdir('Nginx', nginx_pid.strip())
            if ret:
                all_log['nginx'] = ret
            else:
                all_log['nginx'] = ['无']
        else:
            all_log['nginx'] = ['无']
    except Exception,e:
        print e
        logging.error(str(e))
        all_log['nginx'] = ['无']

    try:
        p = subprocess.Popen("ps -C httpd -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                             shell=True)
        ret = p.communicate()
        if ret[0]:
            apache_pid = ret[0]
            ret = getlogdir('Apache', apache_pid.strip())
            if ret:
                all_log['httpd'] = ret
            else:
                all_log['httpd'] = ['无']
        else:
            all_log['httpd'] = ['无']
    except Exception,e:
        print e
        logging.error(str(e))
        all_log['httpd'] = ['无']

    # MySQL日志文件
    try:
        p = subprocess.Popen("ps -C mysqld -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                             shell=True)
        ret = p.communicate()
        if ret[0]:
            mysql_pid = ret[0]
            ret = getDBLog('MySQL', mysql_pid.strip())
            if ret:
                all_log['mysqld'] = ret
            else:
                all_log['mysqld'] = ['无']
        else:
            all_log['mysqld'] = ['无']
    except Exception,e:
        print e
        logging.error(str(e))
        all_log['mysqld'] = ['无']

    # mongodb
    try:
        p = subprocess.Popen("ps -C mongod -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                             shell=True)
        ret = p.communicate()
        if ret[0]:
            mongo_pid = ret[0]
            ret = getDBLog('Mongo', mongo_pid.strip())
            if ret:
                all_log['mongodb'] = ret
            else:
                all_log['mongodb'] = ['无']
        else:
            all_log['mongodb'] = ['无']

        # redis
        ret = getRedisData()
        if ret:
            all_log['redis'] = ret
        else:
            all_log['redis'] = ['无']
    except Exception,e:
        print e
        logging.error(str(e))
        all_log['redis'] = ['无']


    # 网站源码
    documentpath = []
    try:
        # apache部分
        p = subprocess.Popen("ps -C httpd -o pid,user --no-header | head -1 | awk '{print $1}'",
                                 stdout=subprocess.PIPE,
                                 shell=True)
        ret = p.communicate()
        if ret[0]:
            httpd_pid = ret[0].replace('\n', '').replace('\r', '')
            p = subprocess.Popen("ls -l /proc/%s/exe | awk -F '->' '{print $2}'" % httpd_pid,
                                 stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            path_httpd = ret[0].replace('\n', '').replace('\r', '')

            p = subprocess.Popen("%s -V | grep HTTPD_ROOT | awk -F '=' '{print $2}'" % path_httpd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
            ret = p.communicate()
            if ret[0]:
                httpd_root = ret[0].replace('\n', '').replace('\r', '').replace('"','')
                p = subprocess.Popen("%s -V | grep SERVER_CONFIG_FILE | awk -F '=' '{print $2}'" % path_httpd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                ret = p.communicate()
                if ret[0]:
                    server_config_file = ret[0].replace('\n', '').replace('\r', '').replace('"','')
                    config_file = httpd_root + '/' +server_config_file
                    for i in getAllPath(config_file, 'DocumentRoot', 'Include'):
                            documentpath.append(i)
                    # # 获取所有含有documentroot的行
                    # p = subprocess.Popen("cat %s | grep DocumentRoot" % config_file , stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    # ret = p.communicate()
                    # for line in set(ret[0].split('\n')):
                    #     # 排除无用documentroot行
                    #     if line.strip().startswith('DocumentRoot'):
                    #         # 获取路径
                    #         h = line.strip().split(' ')[1].replace('"','').replace(' ','')
                    #         # 相对路径的可能
                    #         if not h.startswith('/'):
                    #             h = config_file.replace('httpd.conf','') + h                             
                    #         documentpath.append(h)

                    # # include 的其他配置的文件
                    # p = subprocess.Popen("cat %s | grep ^Include | awk '{print $2}'" % config_file , stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    # ret = p.communicate()
                    # for i in set(ret[0].strip().replace('"','').split('\n')):
                    #     if not i.startswith('/'):
                    #         i = httpd_root + '/' + i
                    #         i_dir = os.path.dirname(i) 
                    #         if os.path.exists(i_dir):
                    #             conf_list = os.listdir(i_dir)
                    #             for fn in conf_list:# fn 文件名
                    #                 if fn.endswith('.conf'):
                    #                     # 检查内容
                    #                     _f = file(i_dir + '/' + fn)
                    #                     content = _f.readlines()
                    #                     for line in content:
                    #                         if line.strip().startswith('DocumentRoot'):
                    #                             # 获取路径
                    #                             h = line.strip().split(' ')[1].replace('"','').replace(' ','')
                    #                             # 相对路径的可能
                    #                             if not h.startswith('/'):
                    #                                 h = i_dir + '/' + h                             
                    #                             documentpath.append(h)
    except Exception,e:
        print e
        logging.error(str(e))

    try:
        # nginx_website部分
        documentpath_nginx = []

        p = subprocess.Popen("ps -C nginx -o pid,user --no-header | head -1 | awk '{print $1}'",
                                 stdout=subprocess.PIPE,
                                 shell=True)
        ret = p.communicate()
        if ret[0]:
            nginx_pid = ret[0].replace('\n', '').replace('\r', '')
            p = subprocess.Popen("ls -l /proc/%s/exe | awk -F '->' '{print $2}'" % nginx_pid,
                                 stdout=subprocess.PIPE,
                                 shell=True)
            ret = p.communicate()
            if ret[0]:
                path_nginx = ret[0].replace('\n', '').replace('\r', '')
                # 获取nginx.conf位置
                p = subprocess.Popen("%s -t" % path_nginx, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                ret = p.communicate()
                if ret:
                    config_file = ''
                    for i in str(ret).split(' '):
                        if 'nginx.conf' in i:
                            config_file = i
                            break
                    if config_file:
                        for i in getAllPath(config_file, 'root', 'include'):
                            documentpath_nginx.append(i)

                        # # 查找location下root路径
                        # f = file(config_file)
                        # content = f.readlines()
                        # for line in content:
                        #     if 'root' in line and not line.strip().startswith('#'):

                        #         m = re.search(r'[^\s]+;', line)
                        #         if m :
                        #             documentpath_nginx.append(m.group().replace(';', ''))
                        # f.close()
                        # logging.info('nginx.conf中找到root:%s' % str(documentpath_nginx))
                        # #查询另一个文件 include
                        # dirname = []# 其他配置文件的目录
                        # for line in file(config_file).readlines():
                        #     line = line.strip().replace('\n', '').replace(';', '')
                        #     if 'include ' in line and line.endswith('.conf'):
                        #         for i in line.split(' '):
                        #             if i.endswith('.conf'):
                        #                 # dirname = os.path.dirname(i)
                        #                 dirname.append(os.path.dirname(i))
                        # logging.info('nginx其他配置文件路径:%s' % str(dirname))
                        # if dirname:
                        #     for i in dirname:
                        #         # 相对路径的可能
                        #         if i.startswith('/'):
                        #             if os.path.exists(i):
                        #                 conf_list = os.listdir(i)

                        #                 for f in conf_list:
                        #                     if f.endswith('.conf'):
                        #                         # 检查内容
                        #                         _f = file(i + '/' +f)
                        #                         content = _f.readlines()
                        #                         for line in content:
                        #                             if 'root' in line and not line.strip().startswith('#'):
                        #                                 # print '符合条件的行：%s' % line
                        #                                 m = re.search(r'[^\s]+;', line)
                        #                                 if m :
                        #                                     documentpath_nginx.append(m.group().replace(';', ''))
                        #         else:# 相对路径
                        #             relapath = config_file.replace('nginx.conf') + dirname
                        #             if os.path.exists(i):
                        #                 conf_list = os.listdir(i)

                        #                 for f in conf_list:
                        #                     if f.endswith('.conf'):
                        #                         # 检查内容
                        #                         _f = file(i + '/' +f)
                        #                         content = _f.readlines()
                        #                         for line in content:
                        #                             if 'root' in line and not line.strip().startswith('#'):
                        #                                 # print '符合条件的行：%s' % line
                        #                                 m = re.search(r'[^\s]+;', line)
                        #                                 if m :
                        #                                     documentpath_nginx.append(m.group().replace(';', ''))

                        logging.info('nginx所有root:%s' % str(documentpath_nginx))
        for i in set(documentpath_nginx):
            documentpath.append(i)
    except Exception,e:
        print e
        logging.error(str(e))
        # documentpath = ['无']
    if not documentpath:
        documentpath = ['无']
    all_log['website'] = documentpath

    # 系统日志文件
    # for logfile in listsyslogs():
    #     all_log['sys'] = logfile
    all_log['sys'] = listsyslogs()
    return all_log




'''
mainpath:主配置文件地址
include:其他配置文件设置的参数
root:寻找的目标路径的参数

'''
def getAllPath(mainpath, root, include):
    root_length = len(root)
    include_length = len(include)
    documentpath = []
    
    if os.path.exists(mainpath) and not os.path.isdir(mainpath):
        main = file(mainpath)
        # 配置文件的文件夹路径
        main_dir = os.path.dirname(mainpath)

        lines = main.readlines()
        for line in lines:
            line = line.strip().replace(';', '')
            # 找到其他设置配置文件的路径
            if line.startswith(include) and line.endswith('.conf'):
                path = line[include_length:].replace('"','').replace(';','').replace(' ','')
                if not path.startswith('/'):# 相对路径
                    path = main_dir + '/' + path

                if not os.path.exists(path):# 尝试再上一级目录
                    path = os.path.dirname(path)
                if os.path.exists(path):# 
                    if os.path.isdir(path):
                        filelist = os.listdir(path)
                        for filename in filelist:
                            filepath = path + '/' +filename
                            if not os.path.isdir(filepath):
                                for i in getAllPath(filepath, root, include):
                                    documentpath.append(i)
                            else:
                                logging.error('其他配置文件是文件夹：：%s ' % filepath)
                else:
                    logging.error('其他配置文件路径：%s 不存在 ' % path)
            # 找root路径
            if line.startswith(root):
                # path = line.replace('"').replace(';', '').replace(' ','')
                
                path = line[root_length:].replace('"','').replace(';','').replace(' ','')
                if not path.startswith('/'):# 相对路径
                    path = main_dir + '/' + path
                documentpath.append(path)

                logging.info('root路径：%s ' % path)
                

    else:
        logging.error('主配置文件路径：%s 不存在 ' % mainpath)

    return documentpath

if __name__ == '__main__':
    print getAllPath('/etc/nginx/nginx.conf', 'root', 'include')