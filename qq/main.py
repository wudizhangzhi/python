#!/usr/bin/python
#coding=utf8

import Queue
import os
import sys
from threading import Thread
from controller.login_controller import LoginControlller
import subprocess
# reload(sys)

class QQ(object):
    '''
    '''
    def __init__(self):
        self.quit_quit = False
        self.switch_queue = Queue.Queue(0)
        self.view_control_map = {
            'login': LoginControlller()
        }
        Thread(target=self._watchdog_switch).start()

    def _watchdog_switch(self):
        '''
        切换页面线程
        '''
        self.view_control_map['login'].run(self.switch_queue)

        while not self.quit_quit:
            key = self.switch_queue.get()
            if key == 'quit_quit':
                self.quit_quit = True
            else:
                self.view_control_map[key].run(self.switch_queue)
        self.quit()
        os._exit(0)

    def quit(self):
        '''
        退出
        '''
        subprocess.call('echo -e "\033[?25h";clear', shell=True)

qq = QQ()