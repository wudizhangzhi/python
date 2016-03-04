#!/usr/bin/python
#coding=utf-8

class _Getch(object):
    def __init__(self):
        try:
            self._impl = _GetchWindows()
        except ImportError:
            try:
                self._impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self._impl = _GetchUnix()

    def __call__(self):
        '''
        当类实现__call__，这个类的对象就变为可以调用的，
        相当于这个类的对象可以当作函数来调用
        '''
        return self._impl()

class _GetchUnix(object):
    def __init__(self):
        import tty
        '''
        setcbreak(fd, when=2)
           Put terminal into a cbreak mode.

        setraw(fd, when=2)
           Put terminal into a raw mode.
        '''
    def __call__(self):
        import sys
        import termios
        import tty
        '''
        tcgetattr(...)
        Get the tty attributes for file descriptor fd
        '''
        fd = sys.stdin.fileno()
        old_setting = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_setting)
        return ch

class _GetchWindows(object):
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class _GetchMacCarbon(object):
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt  # see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what, msg, when, where, mod) = Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)


getch = _Getch()





