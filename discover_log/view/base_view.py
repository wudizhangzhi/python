#!/usr/bin/python
#coding=utf-8
class BaseView(object):
    def __init__(self):
        #获取屏幕宽高
        self.screen_height, self.screen_width = self.linesnum()
        self.display_lines = []
        self.displayline = ''
        self.markline = 0 #箭头标记的行
        self.time = 0
        self.title = ''

    def make_displaylines(self):
        '''
        生成输出的行
        '''
        pass

    def display(self):
        '''
        显示行
        '''
        pass
    def linesnum(self):
        """
        测试屏幕显示行数, 每行字符数

        return: 屏幕高度 int
        屏幕宽度 int
        """
        import os
        env = os.environ

        def ioctl_GWINSZ(fd):
            try:
                import fcntl, termios, struct
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
            '1234'))
            except:
                return
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        # Use get(key[, default]) instead of a try/catch
        # try:
        #    cr = (env['LINES'], env['COLUMNS'])
        # except:
        #    cr = (25, 80)
        return int(cr[0]), int(cr[1])

