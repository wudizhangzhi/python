#!/usr/bin/python
#coding=utf-8

import sys
sys.path.append('..')
import time
import getch
import Queue
from threading import Thread
from view.process_view import Process
from controller.base_controller import BaseController
from view.base_view import BaseView
import sqlite3

class ProcessController(BaseController):
    '''
    '''
    def __init__(self):
        self._bind_view()
        self.quit = False
        self.queue = Queue.Queue(0)

    def _bind_view(self):
        self.view = Process()

    def run(self, switch_queue):
        #用于控制切换界面
        #self.switch_queue = switch_queue
        #self.quit = False
        #Thread(target=self._controller).start()
        #Thread(target=self._watchdog_queue).start()
        #Thread(target=self._wacthdog_process).start()
        try:
            backdir = raw_input('请输入要保存的路径: ')
        except KeyboardInterrupt:
            print "\t\033[41m 程序终止! \033[m\n"
        if backdir.endswith('/'):
            backdir = backdir[::-1]

	# 进度条
        base = BaseView()
        screen_height, screen_width = base.linesnum()
        content = ['']
        per = 0
	# 进度条线程
        def thread_display():
            while True:
                display_lines = ['\r']
                display_lines.append('正在复制' + '\r')
                display_lines.append('')
                # length = len(content)
                # 显示正在复制的内容
                c = content
                half = screen_height / 2
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

        Thread(target=thread_display).start()
        db = sqlite3.connect('../loginfo.db')
        cur = db.cursor()
        cur.execute('SELECT * FROM log_select')
        all_log = cur.fetchall()
	
	#测试代码
        print '开始'
        total = len(all_log)
        num = 0
        for filelog in all_log:
            print filelog
            copyfile(filelog[0], backdir)
            basename = os.path.basename(filelog[0])
            dirname = os.path.dirname(filelog[0])
            targetname = backdir + dirname + '/' + basename
            content.append('复制' + str(filelog) + '-->' + str(targetname))
            num += 1
            per = num * 100 / total
            time.sleep(0.1)

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
                # self.switch_queue.put('quit_quit')
                self.switch_queue.put('bye')

    def _wacthdog_process(self):
        '''
        页面时间的变化
        '''
        while not self.quit:
            self.view.display()
            time.sleep(1)
            self.view.process += 1
            self.q = str(self.quit)

if __name__=='__main__':
    switch_queue = Queue.Queue(0)
    c = ProcessController().run(switch_queue)
