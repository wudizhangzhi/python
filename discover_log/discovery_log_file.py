#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil
import subprocess
import time
import threading


def getlogdir(prefx, pid):
    print '%s日志文件:' % prefx
    p = subprocess.Popen("ls -l /proc/%s/fd | grep '.log$' | awk -F '->' '{print $2}'" % pid, stdout=subprocess.PIPE,
                         shell=True)
    ret = p.communicate()
    if ret:
        logfiles = []
        for logfile in set(re.sub(r' ', '', ret[0]).split('\n')):
            if logfile:
                print logfile
                logfiles.append(logfile)
        return logfiles


def listsyslogs():
    p = subprocess.Popen("ls -l /var/log |grep ^- | awk '{print $9}'", stdout=subprocess.PIPE, shell=True)
    ret = p.communicate()
    if ret:
        logfiles = []
        for logfile in set(re.sub(r' ', '', ret[0]).split('\n')):
            if logfile:
                logfiles.append('/var/log/%s' % logfile)
        return logfiles


def copyfile(filename, backdir):
    try:
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        targetname = backdir + dirname + '/' + basename
        # print '正在复制 %s 到 %s' % (filename, targetname)
        # 判断目录是否存在
        if os.path.exists(backdir + dirname):
            try:
                shutil.copyfile(filename, targetname)
            except Exception, e:
               print e 
               pass
        else:
            os.makedirs(backdir + dirname)
    #except KeyboardInterrupt:
    except Excepiton, e:
        print e
        print "\t\033[41m 程序终止! \033[m\n"
        sys.exit(-1)


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

    # MySQL日志文件
    p = subprocess.Popen("ps -C mysqld -o cmd | grep -o 'log-error=.*.log'", stdout=subprocess.PIPE, shell=True)
    ret = p.communicate()
    if ret[0]:
        ret = ret[0].replace('log-error=', '')
        all_log['mysqld'] = ret
    else:
        all_log['mysqld'] = ['无']

    # 系统日志文件
    # for logfile in listsyslogs():
    #     all_log['sys'] = logfile
    all_log['sys'] = listsyslogs()
    return all_log

def main():
    all_log = []
    p = subprocess.Popen("ps -C nginx -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                         shell=True)
    ret = p.communicate()
    if ret[0]:
        nginx_pid = ret[0]
        ret = getlogdir('Nginx', nginx_pid.strip())
        if ret:
            all_log.extend(ret)
        print

    p = subprocess.Popen("ps -C httpd -o pid,user --no-header | head -1 | awk '{print $1}'", stdout=subprocess.PIPE,
                         shell=True)
    ret = p.communicate()
    if ret[0]:
        apache_pid = ret[0]
        ret = getlogdir('Apache', apache_pid.strip())
        if ret:
            all_log.extend(ret)
        print

    print 'MySQL日志文件:'
    p = subprocess.Popen("ps -C mysqld -o cmd | grep -o 'log-error=.*.log'", stdout=subprocess.PIPE, shell=True)
    ret = p.communicate()
    if ret[0]:
        print ret[0].replace('log-error=', '')

    print '系统日志文件:'
    for logfile in listsyslogs():
        print logfile
        all_log.append(logfile)

    print
    try:
        backdir = raw_input('请输入要保存的路径: ')
    except KeyboardInterrupt:
        print
        print "\t\033[41m 程序终止! \033[m\n"
        sys.exit(-1)

    if backdir.endswith('/'):
        backdir = backdir[::-1]

    # 进度条
    screen_height, screen_width = linesnum()
    content = ['']
    per = 0

    def thread_display():
        while True:
            display_lines = ['\r']
            display_lines.append('正在复制' + '\r')
            display_lines.append('')
            length = len(content)
            c = content
            half = height / 2
            if len(c) > half:
                c = c[-half:]
            for i in c:
                display_lines.append(i)

            if per == 100:
                display_lines.append("\t\033[36m 复制完成! \033[m")
            else:
                display_lines.append('\t\033[36m 完成:' + str(per) + '%\033[m')
            display_lines.append('')
            for i in range(screen_height - len(display_lines) - 3):
                display_lines.append('')
            pos = screen_width * per / 100 - 1
            if pos < 1:
                pos = 1
            display_lines.append('=' * pos + '>')
            display_lines.append('\r')
            print '\n'.join(display_lines)
            if per == 100:
                break
            time.sleep(0.5)

    threading.Thread(target=thread_display).start()

    total = len(all_log)
    num = 0
    for filelog in all_log:
        copyfile(filelog, backdir)
        basename = os.path.basename(filelog)
        dirname = os.path.dirname(filelog)
        targetname = backdir + dirname + '/' + basename
        content.append('复制' + str(filelog) + '-->' + str(targetname))
        num += 1
        per = num * 100 / total
        time.sleep(0.1)

    print
    # print "\t\033[36m 复制完成! \033[m\n";


welcome = [
    '     #####   #     #  #######  #######  ######    #####   ######      #',
    '    #     #  #     #  #        #        #     #  #     #  #     #    # #',
    '    #        #     #  #        #        #     #  #        #     #   #   #',
    '    #        #######  #####    #####    ######    #####   #     #  #     #',
    '    #        #     #  #        #        #   #          #  #     #  #######',
    '    #     #  #     #  #        #        #    #   #     #  #     #  #     #',
    '     #####   #     #  #######  #######  #     #   #####   ######   #     #',
    '\n',
    '                            #        #######   #####',
    '                            #        #     #  #     #',
    '                            #        #     #  #',
    '                            #        #     #  #  ####',
    '                            #        #     #  #     #',
    '                            #        #     #  #     #',
    '                            #######  #######   #####',
    '\n',
    '    #######  #######  ######   #######  #     #   #####   ###   #####    #####',
    '    #        #     #  #     #  #        ##    #  #     #   #   #     #  #     #',
    '    #        #     #  #     #  #        # #   #  #         #   #        #',
    '    #####    #     #  ######   #####    #  #  #   #####    #   #         #####',
    '    #        #     #  #   #    #        #   # #        #   #   #              #',
    '    #        #     #  #    #   #        #    ##  #     #   #   #     #  #     #',
    '    #        #######  #     #  #######  #     #   #####   ###   #####    #####',
]
# 欢迎界面显示时间
time_welcome = 3

if __name__ == '__main__':
    # 欢迎界面
    height, width = linesnum()
    print '\r'
    top_margin = (height - len(welcome)) / 2
    left_margin = (width - len(welcome[-2])) / 2
    print '\n' * top_margin
    for i in welcome:
        print ' ' * left_margin + i
    print '\n' * (height - top_margin - len(welcome))
    # 欢迎界面结束
    time.sleep(time_welcome)
    uid = os.getuid()
    if uid != 0:
        print '请使用root用户操作'
        sys.exit(-1)
    main()
