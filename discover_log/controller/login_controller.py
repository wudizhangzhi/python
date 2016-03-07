#!/usr/bin/python
#coding=utf-8

import sys
sys.path.append('..')

import time
import getch
import Queue
import sqlite3
from threading import Thread
from view.login_view import Login
from discovery_log_file import *

log_list = ['nginx','httpd','mysqld','sys']


class LoginController(object):
    '''
    '''
    def __init__(self):
        self._bind_view()
        self.quit = False
        self.queue = Queue.Queue(0)
        self.select = 0

    def _bind_view(self):
        self.view = Login()

    def run(self, switch_queue):
        #用于控制切换界面
        self.switch_queue = switch_queue
        self.quit = False
        Thread(target=self._controller).start()
        Thread(target=self._watchdog_queue).start()
        Thread(target=self._wacthdog_time).start()
        # Thread(target=self._discover_log).start()

    def _controller(self):
        '''
        按键监控
        '''
        while not self.quit:
            k = getch.getch()
            self.queue.put(k)
            #
            # if k == 'q' or k == 'o':
            #    break
            if k == 'o':
                break
            if k == 'q':
                if self.view.logshow == False:
                    break

    def _watchdog_queue(self):
        '''
        从queue里取出字符执行命令
        '''
        while not self.quit:
            k = self.queue.get()
            if k == 'q':
                if self.view.logshow == True:# 返回主菜单
                    self.view.logshow = False
                    self.select = 0
                    self.view.select = 0
                else:# 退出界面
                    self.quit = True
                    # self.switch_queue.put('quit_quit')
                    self.switch_queue.put('bye')
            elif k == ' ':# 确定
                self.view.log_name = log_list[self.view.select]
                self.view.changelogfile(get_all_log()[log_list[self.view.select]])
                self.view.logshow = True
                self.view.select = 0
                # self.quit = True
                # self.switch_queue.put('process')
            elif k == 'j':#下
                self.view.move(-1)
                # self.select +=1
            elif k == 'k':#上
                # self.select -=1
                self.view.move(1)
            elif k == 'm':# 标记
                self.view.marking()
            #elif k == 'b':# 返回主页面
            #    self.view.logshow = False
            #    self.select = 0
            #    self.view.select = 0
            elif k =='o':#输入输出地址，然后输出
                self.quit = True
                self.switch_queue.put('rawinput')


    def _wacthdog_time(self):
        '''
        页面时间的变化
        '''
        while not self.quit:
            self.view.display()
            # if self.select < 0:
            #     selk.select = 0
            # elif self.select>3:
            #     self.select = 3
            # self.view.select = self.select
            time.sleep(0.3)

    def _show_logfile(self, index):
        log_list = ['nginx','httpd','mysqld','sys']









if __name__=='__main__':
    q = Queue.Queue(0)
    LoginController().run(q)
