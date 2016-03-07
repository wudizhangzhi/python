#!/usr/bin/python
#coding=utf-8

import sys
sys.path.append('..')

import time
import getch
import Queue
import sqlite3
from threading import Thread
from view.main_view import Main
from discovery_log_file import *

log_list = ['nginx','httpd','mysqld','sys']


class MainController(object):
    '''
    '''
    def __init__(self):
        self._bind_view()
        self.quit = False
        self.queue = Queue.Queue(0)
        self.select = 0

    def _bind_view(self):
        self.view = Main()

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
            if k == ' ':
                break
            if k == 'q':
                break

    def _watchdog_queue(self):
        '''
        从queue里取出字符执行命令
        '''
        while not self.quit:
            k = self.queue.get()
            if k == 'q':
                self.quit = True
                self.switch_queue.put('bye')
            elif k == ' ':# 确定
                if self.view.select == 0:# 全部选择,进入输出界面
                    db = sqlite3.connect('loginfo.db')
                    cur = db.cursor()
                    data = get_all_log()
                    r = []
                    for key in log_list:
                        if data[key][0]!='无':
                            for i in data[key]:
                                t = []
                                t.append(i)
                                r.append(t)
                    cur.executemany('INSERT INTO log_select(name) VALUES(?)', r)
                    db.commit()
                    cur.close()
                    db.close()
                    self.quit = True
                    self.switch_queue.put('rawinput')
                elif self.view.select ==1:# 进入具体界面
                    self.quit = True
                    self.switch_queue.put('login')
            elif k == 'j':#下
                self.view.move(-1)
                # self.select +=1
            elif k == 'k':#上
                # self.select -=1
                self.view.move(1)
            # elif k == 'm':# 标记
            #     self.view.marking()
            # elif k =='o':#输入输出地址，然后输出
            #     self.quit = True
            #     self.switch_queue.put('rawinput')


    def _wacthdog_time(self):
        '''
        页面时间的变化
        '''
        while not self.quit:
            self.view.display()
            time.sleep(0.3)







if __name__=='__main__':
    q = Queue.Queue(0)
    MainController().run(q)
