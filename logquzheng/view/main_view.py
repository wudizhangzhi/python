#!/usr/bin/python
# coding=utf-8
import sys

sys.path.append('..')
from view.base_view import BaseView
from view.sets import *
from utils.methods import get_all_log
import subprocess
import re


# version = 'Linux&&Unix日志取证大师V1.0'

# selection = ['全部日志获取','自定义选择日志']

# line_help = 'q--返回上一页,退出 空格--选择 k--向下  j--向上'


class Main(BaseView):
    def __init__(self):
        # 获取屏幕宽高
        super(Main, self).__init__()
        self.title = '主界面'
        self.content = '请选择...'
        #
        self.select = 0
        self._initSysInfo()

    # def _initSysInfo(self):
    #     memuse, memtotal = calcMemUsage()
    #     import platform
    #     l = ['系统版本: ' + ' '.join(platform.linux_distribution()) + '\r']
    #     l.append('CPU 架构: '+ str(platform.machine()) + '\r')
    #     p = subprocess.Popen('cat /proc/cpuinfo | grep "^model name" | head -1 | awk -F ":" \'{print $2}\'', stdout=subprocess.PIPE,shell=True)
    #     ret = p.communicate()
    #     infos = []
    #     if ret:
    #         for info in set(re.sub(r' ', '', ret[0]).split('\n')):
    #             if info:
    #                 infos.append(info)
    #     l.append('内存使用: ' + str(memuse / 1024) + ' Mb\r')
    #     l.append('内存总量: ' + str(memtotal / 1024) + ' Mb\r')
    #     l.append('CPU 型号: ' + str(infos[0]) + '\r')
    #     self.sysinfo = l


    def make_displaylines(self):
        self.screen_height, self.screen_width = self.linesnum()
        display_lines = ['\r']
        # display_lines.append('')
        # display_lines.append(version + '\r')
        # display_lines.append('')
        width_sys = len(self.sysinfo[0].decode('utf8'))
        self.left_margin = self.screen_width / 2 - width_sys / 2
        for i in self.sysinfo:
            display_lines.append(' ' * self.left_margin + i)
        display_lines.append('')
        display_lines.append(' ' * self.left_margin + self.title + '\r')
        display_lines.append('')

        display_lines.append(' ' * self.left_margin + self.content + '\r')

        for i in range(2):
            if i == self.select:
                line = '->' + ' ' * 10 + '\033[42;37m' + selection[i] + ' \033[0m\r'
            else:
                line = ' ' * 12 + selection[i] + '\r'
            display_lines.append(' ' * self.left_margin + line)
        display_lines.append('')
        for i in range(self.screen_height - len(display_lines) - 2):
            display_lines.append('')

        display_lines.append(line_help)
        display_lines.append('\r')
        self.display_lines = display_lines

    def display(self):
        '''
        显示行
        '''
        self.make_displaylines()
        print '\n'.join(self.display_lines)

    def move(self, step):
        num = self.select + step
        if num < 0:
            self.select = 0
        elif num > 1:
            self.select = 1
        else:
            self.select = num
