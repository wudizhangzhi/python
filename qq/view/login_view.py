#!/usr/bin/python
#coding=utf-8

#from qq.view.base_view.py import base_view

from view.base_view import BaseView
'''



'''

class Login(BaseView):
    def __init__(self):
        super(Login, self).__init__()
        self.title = '欢迎登录界面'
        self.content = '访问网页...'
        self.time = 0

    def make_displaylines(self):
        self.screen_height, self.screen_width = self.linesnum()
        display_lines = ['']
        
        display_lines.append(self.title + '\r')
        display_lines.append('')
        display_lines.append(self.content)
        display_lines.append(str(self.time))
        display_lines.append('')
        for i in range(self.screen_height - len(display_lines) - 1):
        	display_lines.append('')
        self.display_lines = display_lines

    def display(self):
        self.make_displaylines()
        print '\n'.join(self.display_lines)

# if __name__ == '__main__':
#     print '\n'*20
#     win = Login()
#     win.display()


