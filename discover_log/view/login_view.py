#!/usr/bin/python
# coding=utf-8

# from qq.view.base_view.py import base_view
import sys

sys.path.append('..')
from view.base_view import BaseView
from discovery_log_file import get_all_log, calcMemUsage
# from termcolor import colored
import sqlite3

# log文件显示行数
line_show = 15
log_list = ['nginx', 'httpd', 'mysqld', 'sys']

line_help = 'q--返回上一页,退出  o--输出日志  空格--进入  m--标记  k--向下  j--向上'

version = 'Linux&&Unix日志取证大师V1.0'


class Login(BaseView):
    '''
    主界面
    '''

    def __init__(self):
        super(Login, self).__init__()
        self.title = '自定义选择界面'
        self.content = '请选择...'
        self.log_name = ''
        self.content_main = ['\r']
        # 指针
        self.select = 0
        # 指针范围
        self.select_range = len(log_list) - 1
        self.logshow = False
        # log文件开始坐标
        self.logshow_start = 0
        self.logfile = ['无']
        # 具体文件的标记
        self.mark = {'nginx': [], 'httpd': [], 'mysqld': [], 'sys': []}
        # 主页面的标记
        self.mark_main = []
        # 是否正在进行数据库操作
        self.working = False
        # 
        self._initSysInfo()
        # self.memuse, self.memtotal = calcMemUsage()

    def _initSysInfo(self):
        memuse, memtotal = calcMemUsage()
        import platform 
        l = ['系统:' + str(platform.platform()) + '\r']
        l.append('内存使用:' + str(memuse) + ' kb  内存总共:' + str(memtotal) + ' kb\r')
        l.append('计算机类型:'+ str(platform.machine()) + '\r')
        l.append('处理器信息:' + str(platform.processor()) + '\r')
        self.sysinfo = l

    def make_displaylines(self):
        self.screen_height, self.screen_width = self.linesnum()
        display_lines = ['\r']
        display_lines.append('\033[34m' + version + ' \033[0m' + '\r')
        display_lines.append(self.title + ' ' * 10 + self.log_name + '\r')
        display_lines.append('')
        # display_lines.append('内存使用:' + str(self.memuse) + ' kb  内存总共:' + str(self.memtotal) + ' kb\r')
        for i in self.sysinfo:
            display_lines.append(i)
        display_lines.append('')

        display_lines.append(self.content + str(self.select) + '\r')
        if not self.logshow:
            # 重置指针范围
            self.select_range = len(log_list)
            for i in range(len(log_list)):
                if i == self.select:
                    line = '->' + ' ' * 10 + '\033[42;37m' + log_list[i] + '\033[0m'
                    # display_lines.append('->' +' '*10 +log_list[i]+ '\r')
                else:
                    line = ' ' * 12 + log_list[i]
                    # display_lines.append(' '*12 +log_list[i]+ '\r')
                if i in self.mark_main:  # 标记
                    line += '   \033[36m√ \033[0m'
                line += '\r'
                display_lines.append(line)

        else:  # 显示具体文件内容
            # log = get_all_log()[log_list[self.select]]
            self.select_range = len(self.logfile)
            # 显示的部分
            if self.select > line_show - 1:
                self.logshow_start = self.select - line_show + 1
            if self.select < line_show:
                self.logshow_start = 0

            if self.select_range < line_show:
                logshow_end = self.select_range
            else:
                logshow_end = self.logshow_start + line_show
            for i in range(self.logshow_start, logshow_end):
                if i == self.select:
                    line = '->' + ' ' * 10 + self.logfile[i]
                else:
                    line = ' ' * 12 + self.logfile[i]
                if i in self.mark[self.log_name]:  # 标记
                    line += '    \033[36m√ \033[0m'
                line += '\r'
                display_lines.append(line)
        #display_lines.append(' ' * 12 + str(self.select) + '\r')

        display_lines.append('')
        for i in range(self.screen_height - len(display_lines) - 2):
            display_lines.append('')
        # 帮助信息
        display_lines.append(line_help)
        display_lines.append('\r')
        self.display_lines = display_lines

    def display(self):
        self.make_displaylines()
        print '\n'.join(self.display_lines)

    def move(self, step):
        num = self.select + step
        if num < 0:
            self.select = 0
        elif num > self.select_range -1:
            self.select = self.select_range - 1
        else:
            self.select = num

    def changelogfile(self, logfile):
        self.logfile = logfile

    def marking(self):
        if not self.working:
            self.working = True
            db = sqlite3.connect('loginfo.db')
            cur = db.cursor()
            if self.logshow:
                filename = self.logfile[self.select]
                if self.select in self.mark[self.log_name]:
                    self.mark[self.log_name].remove(self.select)
                    cur.execute('delete from log_select where name="%s"' % filename)
                else:
                    self.mark[self.log_name].append(self.select)
                    filename = self.logfile[self.select]
                    cur.execute('insert into log_select(name) values("%s")' % filename)
            else:
                data = get_all_log()[log_list[self.select]]
                r = []
                for i in data:
                    t = []
                    t.append(i)
                    r.append(t)
                if r and r[0][0]!='无':
                    if self.select in self.mark_main:
                        self.mark_main.remove(self.select)
                        cur.executemany('DELETE FROM log_select WHERE name=?', r)
                    else:
                        self.mark_main.append(self.select)
                        cur.executemany('INSERT INTO log_select(name) VALUES(?)', r)
            db.commit()
            cur.close()
            db.close()
            self.working = False


if __name__ == '__main__':
    win = Login()
    win.display()
