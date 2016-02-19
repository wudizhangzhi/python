#!/usr/bin/python
#coding=utf-8

import time
import getch
import Queue
from threading import Thread
import getch
from view.login_view import Login

class LoginControlller(object):
    '''
    '''
    def __init__(self):
        self._bind_view()
        self.quit = False
        self.queue = Queue.Queue(0)

    def _bind_view(self):
        self.view = Login()

    def run(self, switch_queue):
        #用于控制切换界面
        self.switch_queue = switch_queue
        self.quit = False
        Thread(target=self._controller).start()
        Thread(target=self._watchdog_queue).start()
        Thread(target=self._wacthdog_time).start()

    def _controller(self):
        '''
        按键监控
        '''
        while not self.quit:
            k = getch.getch()
            self.queue.put(k)
            #
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
                self.switch_queue.put('quit_quit')

    def _wacthdog_time(self):
        while not self.quit:
            self.view.display()
            time.sleep(1)
            self.view.time += 1
