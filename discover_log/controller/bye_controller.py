#!/usr/bin/python
#coding=utf8
import sys
sys.path.append('..')
from view.bye_view import Bye
import getch
from controller.base_controller import BaseController
from threading import Thread

class ByeController(BaseController):
    def __init__(self):
        super(ByeController, self).__init__()

    def _bind_view(self):
        self.view = Bye()

    def _controller(self):
        '''
        按键监控
        '''
        # while not self.quit:
        k = getch.getch()
        self.queue.put(k)
        
        # if k == 'q':
            # break

    def _watchdog_queue(self):
        '''
        从queue里取出字符执行命令
        '''
        # while not self.quit:
        k = self.queue.get()
        if k == 'q':
            self.switch_queue.put('quit_quit')
        else:
            self.switch_queue.put('main')
        self.quit = True
