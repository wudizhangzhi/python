#!/usr/bin/python
# coding=utf-8
from utils.methods import calcMemUsage
from view.sets import *
import subprocess
import re


class BaseView(object):
    def __init__(self):
        # 获取屏幕宽高
        self.screen_height, self.screen_width = self.linesnum()
        self.display_lines = []
        self.displayline = ''
        self.markline = 0  # 箭头标记的行
        self.time = 0
        self.title = ''

    def make_displaylines(self):
        '''
        生成输出的行
        '''
        pass

    def display(self):
        '''
        显示行
        '''
        pass

    def linesnum(self):
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

        # Use get(key[, default]) instead of a try/catch
        # try:
        #    cr = (env['LINES'], env['COLUMNS'])
        # except:
        #    cr = (25, 80)
        return int(cr[0]), int(cr[1])

    def _initSysInfo(self):
        memuse, memtotal = calcMemUsage()
        import platform
        # l = ['系统版本: ' + ' '.join(platform.linux_distribution()) + '\r']
        l = []
        # l.append('CPU 架构: '+ str(platform.machine()) + '\r')
        p = subprocess.Popen('cat /proc/cpuinfo | grep "^model name" | head -1 | awk -F ":" \'{print $2}\'',
                             stdout=subprocess.PIPE, shell=True)
        ret = p.communicate()
        infos = []
        if ret:
            for info in set(re.sub(r' ', '', ret[0]).split('\n')):
                if info:
                    infos.append(info)

        p = subprocess.Popen('cat /etc/issue.net | head -1',
                             stdout=subprocess.PIPE, shell=True)
        ret = p.communicate()
        if ret[0]:
            sysinfo = ret[0].strip()
        else:
            sysinfo = ' '.join(platform.linux_distribution())

        line1 = '|' + version
        line2 = '|系统版本: ' + sysinfo
        line3 = '|CPU 架构: ' + str(platform.machine())
        line4 = '|内存使用: ' + str(memuse / 1024) + ' Mb'
        line5 = '|内存总量: ' + str(memtotal / 1024) + ' Mb'
        line6 = '|CPU 型号: ' + str(infos[0])
        width_border = len(line6.decode('utf8')) + 2
        # l.append('◤'+'-'*width_border+'◥\r')
        # l.append('|'+ version + '\r')
        # l.append('+'+'-'*width_border+'+\r')
        # l.append('|系统版本: ' + ' '.join(platform.linux_distribution()) + '\r')
        # l.append('|CPU 架构: '+ str(platform.machine()) + '\r')
        # l.append('|内存使用: ' + str(memuse / 1024) + ' Mb\r')
        # l.append('|内存总量: ' + str(memtotal / 1024) + ' Mb\r')
        # l.append('|CPU 型号: ' + str(infos[0]) + '\r')
        # l.append('◣'+'-'*width_border+'◢\r')
        l.append('●' + '■' * width_border + '●\r')
        l.append(line1 + ' ' * (width_border - 27) + '|\r')
        l.append('+' + '-' * width_border + '+\r')
        l.append(line2 + ' ' * (width_border - len(line2.decode('utf8')) - 4) + ' |\r')
        l.append(line3 + ' ' * (width_border - len(line3.decode('utf8')) - 2) + ' |\r')
        l.append(line4 + ' ' * (width_border - len(line4.decode('utf8')) - 4) + ' |\r')
        l.append(line5 + ' ' * (width_border - len(line5.decode('utf8')) - 4) + ' |\r')
        l.append(line6 + ' |\r')
        l.append('●' + '■' * width_border + '●\r')
        self.sysinfo = l
