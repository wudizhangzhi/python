#!/usr/bin/python
#coding=utf-8
from view.base_view import BaseView
# from termcolor import colored


class Bye(BaseView):
    '''
    退出界面
    '''
    def __init__(self):
        super(Bye, self).__init__()
        # self.title = '退出界面'
        self.info = '\033[31m (╭￣3￣)╭♡ \033[0m' + ' \033[32m退出(q)?\033[0m'

    def make_displaylines(self):
        self.screen_height, self.screen_width = self.linesnum()
        display_lines = ['\r']

        # display_lines.append(self.title + '\r')
        display_lines.append('')
        for i in range(self.screen_height - len(display_lines) - 2):
            if i == self.screen_height / 2:
                display_lines.append(' ' * ((self.screen_width - 18)/2) + self.info + '\r')
            else:
                display_lines.append('')
        display_lines.append('\r')
        self.display_lines = display_lines

    def display(self):
        self.make_displaylines()
        print '\n'.join(self.display_lines)

