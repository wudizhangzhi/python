#!/usr/bin/python
# coding=utf-8

from view.base_view import BaseView


class Process(BaseView):
    '''
    登录界面
    '''

    def __init__(self):
        super(Process, self).__init__()
        self.title = '进度界面'
        self.content = '进度...'
        self.process = 0
        self.q = 'false'

    def make_displaylines(self):
        self.screen_height, self.screen_width = self.linesnum()
        display_lines = ['\r']
        display_lines.append(self.title + '\r')
        display_lines.append('')
        display_lines.append(self.content)
        display_lines.append(str(self.process) + '%;' + self.q)
        display_lines.append('')
        for i in range(self.screen_height - len(display_lines) - 2):
            display_lines.append('')
        display_lines.append('\r')
        self.display_lines = display_lines

    def display(self):
        self.make_displaylines()
        print '\n'.join(self.display_lines)
