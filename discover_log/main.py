#!/usr/bin/python
# coding=utf8

import Queue
import os
import sys
from threading import Thread
from controller.login_controller import LoginController
from controller.bye_controller import ByeController
from controller.process_controller import ProcessController
from view.base_view import BaseView
from discovery_log_file import *
import sqlite3
import subprocess
import time

'''
欢迎界面
主界面：选择，进入，开始
具体文件界面：选择
输入目录界面：输入目录
输出界面：显示进度条
'''


class QQ(object):
    '''
    '''

    def __init__(self):
        self.quit_quit = False
        self.switch_queue = Queue.Queue(0)
        self.view_control_map = {
            'login': LoginController(),
            'bye': ByeController(),
            'process': ProcessController(),
        }
        self._init_db()

        Thread(target=self._watchdog_switch).start()

    def _init_db(self):
        db = sqlite3.connect('loginfo.db')
        cur = db.cursor()
        # cur.execte('drop table if exists discover_log')
        # cur.execute('create table if not exists discover_log(id integer primary key autoincrement,name varchar(10))')
        # keys = [(1,'nginx'),(2,'httpd'),(3,'mysqld'),(4,'sys')]
        # sql = 'insert into discover_log values(?,?)'
        # cur.executemany(sql, keys)
        # cur.execute('drop table if exists discover_logfile')
        # cur.execute('create table if not exists discover_logfile(id integer primary key autoincrement,filename text,type integer)')
        cur.execute('DROP TABLE IF EXISTS log_select')
        cur.execute('CREATE TABLE IF NOT EXISTS log_select(name TEXT)')
        db.commit()
        cur.close()
        db.close()

    def _watchdog_switch(self):
        '''
        切换页面线程
        '''
        self.view_control_map['login'].run(self.switch_queue)

        while not self.quit_quit:
            key = self.switch_queue.get()
            if key == 'quit_quit':
                self.quit_quit = True
            elif key == 'rawinput':
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
                db = sqlite3.connect('loginfo.db')
                cur = db.cursor()
                cur.execute('SELECT * FROM log_select')
                all_log = cur.fetchall()

                #测试代码
                total = len(all_log)
                num = 0
                for filelog in all_log:
                    copyfile(filelog[0], backdir)
                    basename = os.path.basename(filelog[0])
                    dirname = os.path.dirname(filelog[0])
                    targetname = backdir + dirname + '/' + basename
                    content.append('复制' + str(filelog) + '-->' + str(targetname))
                    num += 1
                    per = num * 100 / total
                    time.sleep(0.1)
                break
            else:
                self.view_control_map[key].run(self.switch_queue)
                # self.quit()
                # os._exit(0)

    def quit(self):
        '''
        退出
        '''
        subprocess.call('echo -e "\033[?25h";clear', shell=True)


qq = QQ()
