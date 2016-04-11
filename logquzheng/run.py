#!/usr/bin/python
# coding=utf8

import platform
import sys
import os

if __name__ == '__main__':

    uid = os.getuid()
    if uid != 0:
        print '请使用root用户操作'
        sys.exit(-1)

    ret = platform.architecture()
    if ret[0] == '64bit':
        os.chmod('bin64/main64', 0755)
        os.system('bin64/main64')
    else:
        os.chmod('bin32/main32', 0755)
        os.system('bin32/main32')
