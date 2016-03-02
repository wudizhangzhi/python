#!/usr/bin/python
#coding=utf-8

import subprocess
import time
import threading

p = subprocess.Popen('mplayer notice.mp3', shell=True)
def protect(p):
    switch = True
    while switch:
        p.poll()
        print p.returncode, p.pid
        if p.returncode == 0:
            p = subprocess.Popen('mplayer notice.mp3', shell=True)
        input = raw_input()
        if input = ''
        time.sleep(0.5)
pr = threading.Thread(target=protect, args=(p,))
pr.start()
print 'protect start'
