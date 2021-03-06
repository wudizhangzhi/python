#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
数据层
"""
from threading import RLock, Thread
import logging
import functools
import Queue

from doubanfm.API.api import Doubanfm
from doubanfm.API.netease_api import Netease
from doubanfm.config import db_config

logger = logging.getLogger('doubanfm')
douban = Doubanfm()
mutex = RLock()
QUEUE_SIZE = 5


class Playlist(object):
    """
    播放列表, 各个方法互斥

    使用方法:

        playlist = Playlist()

        playingsong = playlist.get_song()

        获取当前播放歌曲
        playingsong = playlist.get_playingsong()
    """

    def __init__(self):
        self._playlist = Queue.Queue(QUEUE_SIZE)
        self._playingsong = None
        self._get_first_song()

        # 根据歌曲来改变歌词
        self._lrc = {}
        self._pre_playingsong = None

        # 会有重复的歌曲避免重复播放
        self.hash_sid = {}

    def lock(func):
        """
        互斥锁
        """
        @functools.wraps(func)
        def _func(*args, **kwargs):
            mutex.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                mutex.release()
        return _func

    def _watchdog(self):
        sid = self._playingsong['sid']
        while 1:

            # 去重
            while 1:
                song = douban.get_song(sid)
                sid = song['sid']
                if song['sid'] not in self.hash_sid:
                    break

            self._playlist.put(song)
            if not self._playingsong:
                self._playlist.get(False)

    @lock
    def _get_first_song(self):
        song = douban.get_first_song()
        self._playlist.put(song)
        self._playingsong = song
        Thread(target=self._watchdog).start()

    def get_lrc(self):
        """
        返回当前播放歌曲歌词
        """
        if self._playingsong != self._pre_playingsong:
            self._lrc = douban.get_lrc(self._playingsong)
            self._pre_playingsong = self._playingsong
        return self._lrc

    def set_channel(self, channel_num):
        """
        设置api发送的FM频道

        :params channel_num: channel_list的索引值 int
        """
        douban.set_channel(channel_num)
        self.empty()
        self._get_first_song()

    def set_song_like(self, playingsong):
        douban.rate_music(playingsong['sid'])

    def set_song_unlike(self, playingsong):
        douban.unrate_music(playingsong['sid'])

    @lock
    def bye(self):
        """
        不再播放, 返回新列表
        """
        douban.bye(self._playingsong['sid'])

    @lock
    def get_song(self, netease=False):
        """
        获取歌曲, 对外统一接口
        """
        song = self._playlist.get(True)
        self.hash_sid[song['sid']] = True  # 去重

        # 网易320k音乐
        if netease:
            url, kbps = Netease().get_url_and_bitrate(song['title'])
            if url and kbps:
                song['url'], song['kbps'] = url, kbps

        self._playingsong = song

        return song

    @lock
    def get_playingsong(self):
        return self._playingsong

    @lock
    def empty(self):
        """
        清空playlist
        """
        self._playingsong = None
        self._playlist = Queue.Queue(QUEUE_SIZE)

    def submit_music(self, playingsong):
        douban.submit_music(playingsong['sid'])


class History(object):

    def __init__(self):
        db_config.history


class Channel(object):

    def __init__(self):
        self.lines = douban.channels
