# -*- coding: utf-8 -*-

import re
import random
import json
import os
import sys
import datetime
import time
import threading
import logging
import urllib
from HttpClient import HttpClient
from  db import mydb

reload(sys)
sys.setdefaultencoding("utf-8")

# HttpClient_Ist = HttpClient()
#
# ClientID = int(random.uniform(111111, 888888))
# PTWebQQ = ''
# APPID = 0
# msgId = 0
# FriendList = {}
# GroupList = {}
# ThreadList = []
# GroupThreadList = []
# GroupWatchList = []
# PSessionID = ''
# Referer = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
SmartQQUrl = 'http://w.qq.com/login.html'


# VFWebQQ = ''
# AdminQQ = '0'
# tulingkey = '#YOUR KEY HERE#'
#
# initTime = time.time()

# logging.basicConfig(filename='log.log', level=logging.DEBUG,
#                     format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S')


# -----------------
# 方法声明
# -----------------

def getHashCode(b, j):
    """
    get the hash num to achieve the grouplist info (record:gcode)

    source function:
        http://0.web.qstatic.com/webqqpic/pubapps/0/50/eqq.all.js
    source function definition:
        P=function(b,j)

    Args:
         b : real QQ num
         j : ptwebqq (get it by cookies)

    Returns:
         string : hashValue
    """
    a = [0, 0, 0, 0]
    for i in range(0, len(j)):
        a[i % 4] ^= ord(j[i])

    w = ["EC", "OK"]
    d = [0, 0, 0, 0]

    d[0] = int(b) >> 24 & 255 ^ ord(w[0][0])
    d[1] = int(b) >> 16 & 255 ^ ord(w[0][1])
    d[2] = int(b) >> 8 & 255 ^ ord(w[1][0])
    d[3] = int(b) & 255 ^ ord(w[1][1])

    w = [0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(0, 8):
        if i % 2 == 0:
            w[i] = a[i >> 1]
        else:
            w[i] = d[i >> 1]
    a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    d = ""

    for i in range(0, len(w)):
        d += a[w[i] >> 4 & 15]
        d += a[w[i] & 15]

    return d


def requestOffpic(file_path, tuin):
    '''下载图片'''
    print file_path, tuin, QQ.ClientID, QQ.PSessionID
    print  QQ.HttpClient_Ist.Get(
        'http://w.qq.com/d/channel/get_offpic2?vfwebqq={0}&tuin={1}&clientid={2}&psessionid={3}'.format(
            file_path,
            tuin,
            QQ.ClientID,
            QQ.PSessionID)
        , refer='http://w.qq.com/')


def combine_msg(content, tuin=None):
    '''判断消息'''
    msgTXT = ""
    for part in content:
        # print type(part)
        if type(part) == type(u'\u0000'):
            msgTXT += part
        elif len(part) > 1:
            # 如果是图片
            if str(part[0]) == "offpic" or str(part[0]) == "cface":
                if str(part[0]) == 'offpic':
                    try:
                        requestOffpic(part[1]['filepath'], tuin)
                    except:
                        print u'下载图片失败'
                msgTXT += "[图片]"
            elif str(part[0]) == "face":
                index = part[1]
                msgTXT += '<img src="/static/img/face/' + str(index) + '.png">'
    return msgTXT


def getReValue(html, rex, er, ex):
    v = re.search(rex, html)

    if v is None:
        logging.error(er)

        if ex:
            raise Exception, er
        return ''

    return v.group(1)


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000


# -----------------
# 主要类
# -----------------

class QQ():
    HttpClient_Ist = HttpClient()

    # ClientID = int(random.uniform(11111111, 88888888))
    ClientID=53999199
    PTWebQQ = ''
    APPID = 0
    msgId = 0
    FriendList = {}
    GroupList = {}
    ThreadList = []
    GroupThreadList = []
    GroupWatchList = ['192795735', '314440865', '18']
    PSessionID = ''
    Referer = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
    # Referer = 'http://d.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
    # SmartQQUrl = 'http://w.qq.com/login.html'
    VFWebQQ = ''
    AdminQQ = '0'
    tulingkey = '6d7bdd3255fb1c940d265f6470b1b641'

    initTime = time.time()

    @classmethod
    def pass_time(cls):
        # global initTime
        rs = (time.time() - QQ.initTime)
        QQ.initTime = time.time()
        return str(round(rs, 3))

    # 查询QQ号，通常首次用时0.2s，以后基本不耗时
    @classmethod
    def uin_to_account(cls, tuin):
        # 如果消息的发送者的真实QQ号码不在FriendList中,则自动去取得真实的QQ号码并保存到缓存中
        # global FriendList,Referer
        if tuin not in QQ.FriendList:
            try:
                t=int(time.time())*1000
                print tuin,QQ.VFWebQQ,t
                print 'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, QQ.VFWebQQ,t)
                info = json.loads(cls.HttpClient_Ist.Get(
                    'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, QQ.VFWebQQ,t),
                    QQ.Referer))
                logging.info("Get uin to account info:" + str(info))
                print u'真实QQ:'+str(info)
                if info['retcode'] != 0:
                    print u'询问真实QQ号出错'
                    raise ValueError, info
                info = info['result']
                QQ.FriendList[tuin] = info['account']
                print u'获得真实QQ号码：' + str(info['account'])

            except Exception as e:
                logging.error(e)

        logging.info(u"Now FriendList:" + str(QQ.FriendList))
        return QQ.FriendList[tuin]

    def getQQnumber(self):
        return self.qqLogin.getqq()

    @classmethod
    def msg_handler(cls, msgObj):
        for msg in msgObj:
            msgType = msg['poll_type']

            # QQ私聊消息
            if msgType == 'message' or msgType == 'sess_message':  # 私聊 or 临时对话
                txt = combine_msg(msg['value']['content'])
                tuin = msg['value']['from_uin']#普通消息QQ号加密后
                msg_id = msg['value']['msg_id2']
                from_account = QQ.uin_to_account(tuin)

                # print "{0}:{1}".format(from_account, txt)
                targetThread = QQ.thread_exist(from_account)
                if targetThread:
                    targetThread.push(txt, msg_id)
                else:
                    try:
                        service_type = 0
                        isSess = 0
                        group_sig = ''
                        if msgType == 'sess_message':
                            isSess = 1
                            service_type = msg['value']['service_type']
                            myid = msg['value']['id']
                            ts = time.time()
                            while ts < 1000000000000:
                                ts = ts * 10
                            ts = int(ts)
                            info = json.loads(QQ.HttpClient_Ist.Get(
                                'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                                    myid, tuin, QQ.ClientID, QQ.PSessionID, service_type, ts), QQ.Referer))
                            logging.info("Get group sig:" + str(info))
                            if info['retcode'] != 0:
                                raise ValueError, info
                            info = info['result']
                            group_sig = info['value']
                        tmpThread = QQ.pmchat_thread(tuin, isSess, group_sig, service_type)
                        tmpThread.start()
                        QQ.ThreadList.append(tmpThread)
                        tmpThread.push(txt, msg_id)
                    except Exception, e:
                        logging.info("error" + str(e))

                        # print "{0}:{1}".format(self.FriendList.get(tuin, 0), txt)

                        # if FriendList.get(tuin, 0) == AdminQQ:#如果消息的发送者与AdminQQ不相同, 则忽略本条消息不往下继续执行
                        #     if txt[0] == '#':
                        #         thread.start_new_thread(self.runCommand, (tuin, txt[1:].strip(), msgId))
                        #         msgId += 1

                        # if txt[0:4] == 'exit':
                        #     logging.info(self.Get('http://d.web2.qq.com/channel/logout2?ids=&clientid={0}&psessionid={1}'.format(self.ClientID, self.PSessionID), Referer))
                        #     exit(0)

            # 群消息
            if msgType == 'group_message':
                # global GroupList, GroupWatchList
                txt = combine_msg(msg['value']['content'])
                guin = msg['value']['from_uin']
                gid = msg['value']['info_seq']
                tuin = msg['value']['send_uin']
                seq = msg['value']['seq']
                QQ.GroupList[guin] = gid
                if str(gid) in QQ.GroupWatchList:
                    g_exist = QQ.group_thread_exist(gid)
                    if g_exist:
                        print u'群线程存在'
                        g_exist.handle(tuin, txt, seq)
                        # g_exist.get_group_list()
                    else:
                        tmpThread = QQ.group_thread(guin)
                        tmpThread.start()
                        QQ.GroupThreadList.append(tmpThread)
                        # tmpThread.get_group_list()
                        tmpThread.handle(tuin, txt, seq)
                        logging.info("群线程已生成")
                        print u'群线已+生成'
                else:
                    logging.info(str(gid) + "群有动态，但是没有被监控")

                    # from_account = uin_to_account(tuin)
                    # print "{0}:{1}".format(from_account, txt)
            if msgType == 'discu_message':
                print u'开始讨论组回复'
                txt = combine_msg(msg['value']['content'])
                guin = msg['value']['from_uin']
                gid = msg['value']['info_seq']
                tuin = msg['value']['send_uin']
                seq = msg['value']['seq']
                QQ.GroupList[guin] = gid
                if str(gid) in QQ.GroupWatchList:
                    g_exist = QQ.discu_thread_exist(gid)
                    if g_exist:
                        print u'群线程存在'
                        g_exist.handle(tuin, txt, seq)
                    else:
                        tmpThread = QQ.discu_thread(guin)
                        tmpThread.start()
                        QQ.GroupThreadList.append(tmpThread)
                        tmpThread.handle(tuin, txt, seq)
                        logging.info("群线程已生成")
                        print u'群线已生成'
                else:
                    logging.info(str(gid) + "群有动态，但是没有被监控")
                pass
            if msgType == 'sys_g_msg':
                if msg['value']['type'] == 'group_request_join':
                    print u'申请加群'
                    from_uin = msg['value']['from_uin']
                    request_uin = msg['value']['request_uin']
                    gcode = msg['value']['gcode']
                    t = QQ.group_check_thread(guin=from_uin, gcode=gcode)
                    t.request_member(request_uin)
                    t.start()
                    print u'监听成员线程已经生成'
                    # 轮询加入uin

                pass
            # QQ号在另一个地方登陆, 被挤下线
            if msgType == 'kick_message':
                logging.error(msg['value']['reason'])
                raise Exception, msg['value']['reason']  # 抛出异常, 重新启动WebQQ, 需重新扫描QRCode来完成登陆

    @classmethod
    def send_msg(cls, tuin, content, isSess, group_sig, service_type):
        if isSess == 0:
            reqURL = "http://d1.web2.qq.com/channel/send_buddy_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(
                     tuin, QQ.ClientID, QQ.msgId, QQ.PSessionID,
                     str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
                         "utf-8"))),
                ('clientid', QQ.ClientID),
                ('psessionid', QQ.PSessionID)
            )

            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            rspp = json.loads(rsp)
            if rspp['retcode'] != 0:
                print u'回复私人消息失败：'+str(rspp)
                # logging.error("reply pmchat error" + str(rspp['retcode']))
        else:
            reqURL = "http://d.web2.qq.com/channel/send_sess_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                     tuin, QQ.ClientID, QQ.msgId, QQ.PSessionID,
                     str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
                         "utf-8"),
                     group_sig, service_type)),
                ('clientid', QQ.ClientID),
                ('psessionid', QQ.PSessionID),
                ('group_sig', group_sig),
                ('service_type', service_type)
            )
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            rspp = json.loads(rsp)
            if rspp['retcode'] != 0:
                print u'回复群消息失败:'+str(rspp)
                # logging.error("reply temp pmchat error" + str(rspp['retcode']))

        return rsp

    @classmethod
    def thread_exist(cls, tqq):
        for t in QQ.ThreadList:
            if t.isAlive():
                if t.tqq == tqq:
                    t.check()
                    return t
            else:
                QQ.ThreadList.remove(t)
        return False

    @classmethod
    def discu_thread_exist(cls, gid):
        for t in QQ.GroupThreadList:
            if str(t.gid) == str(gid):
                return t
        return False

    @classmethod
    def group_thread_exist(cls, gid):
        for t in QQ.GroupThreadList:
            if str(t.gid) == str(gid):
                return t
        return False

    # -----------------
    # 类声明
    # -----------------


    class Login(HttpClient):
        MaxTryTime = 5  # 整体循环检查最大次数：5

        def __init__(self, vpath, qq=0):
            # global APPID, AdminQQ, PTWebQQ, VFWebQQ, PSessionID, msgId,SmartQQUrl,Referer,ClientID

            self.VPath = vpath  # QRCode保存路径
            QQ.AdminQQ = int(qq)
            logging.critical(u"正在获取登陆页面")
            print u'正在获取登陆页面'
            self.initUrl = getReValue(self.Get(SmartQQUrl), r'\.src = "(.+?)"', 'Get Login Url Error.', 1)
            html = self.Get(self.initUrl + '0')

            logging.critical(u"正在获取appid")
            QQ.APPID = getReValue(html, r'g_appid\s*=\s*encodeURIComponent\s*\("(\d+)"', 'Get AppId Error', 1)
            logging.critical(u"正在获取login_sig")
            sign = getReValue(html, r'g_login_sig\s*=\s*encodeURIComponent\s*\("(.+?)"\)', 'Get Login Sign Error', 0)
            logging.info(u'get sign : %s', sign)
            logging.critical("正在获取pt_version")
            JsVer = getReValue(html, r'g_pt_version\s*=\s*encodeURIComponent\s*\("(\d+)"\)', 'Get g_pt_version Error',
                               1)
            logging.info(u'get g_pt_version : %s', JsVer)
            logging.critical(u"正在获取mibao_css")
            MiBaoCss = getReValue(html, r'g_mibao_css\s*=\s*encodeURIComponent\s*\("(.+?)"\)', 'Get g_mibao_css Error',
                                  1)
            logging.info(u'get g_mibao_css : %s', sign)
            StarTime = date_to_millis(datetime.datetime.utcnow())

            # 整体二维码循环最大次数：5
            T = 0
            while True:
                T = T + 1
                self.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(QQ.APPID),
                              self.VPath)

                logging.info(u'[{0}] Get QRCode Picture Success.'.format(T))
                print u'二维码下载:' + str(self.VPath)


                rq_check_time = 0  # 验证码检查20次
                while True:
                    print u'开始监听二维码扫描:' + str(rq_check_time)
                    html = self.Get(
                        'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(
                            QQ.APPID, date_to_millis(datetime.datetime.utcnow()) - StarTime, MiBaoCss, JsVer, sign),
                        self.initUrl)
                    logging.info(html)
                    print u'二维码监听返回:' + str(html)
                    ret = html.split("'")
                    if ret[1] == '65' or ret[1] == '0':  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                        break
                    rq_check_time = rq_check_time + 1
                    if rq_check_time > 20:
                        break
                    time.sleep(2)
                # 如果验证成功 或 整体循环次数>5 或 验证二维码超过20次,退出二维码循环
                if ret[1] == '0' or T > self.MaxTryTime or rq_check_time > 20:
                    print u'退出二维码循环'
                    break

            logging.info(ret)
            if ret[1] != '0':
                # 删除QRCode文件
                if os.path.exists(self.VPath):
                    print u'删除二维码'
                    os.remove(self.VPath)
                raise ValueError, "RetCode = " + ret['retcode']
                return
            logging.critical(u"二维码已扫描，正在登陆")
            print u'二维码已扫描，正在登陆'
            QQ.pass_time()
            # 删除QRCode文件
            if os.path.exists(self.VPath):
                print u'删除二维码'
                os.remove(self.VPath)

            # 记录登陆账号的昵称
            tmpUserName = ret[11]

            html = self.Get(ret[5])
            url = getReValue(html, r' src="(.+?)"', 'Get mibao_res Url Error.', 0)
            if url != '':
                html = self.Get(url.replace('&amp;', '&'))
                url = getReValue(html, r'location\.href="(.+?)"', 'Get Redirect Url Error', 1)
                html = self.Get(url)

            QQ.PTWebQQ = self.getCookie('ptwebqq')

            # logging.info(u'PTWebQQ: {0}'.format(QQ.PTWebQQ))
            print u'PTWebQQ: {0}'.format(QQ.PTWebQQ)

            # TODO 测试获取vfwebqq
            try:
                html=self.Post('http://s.web2.qq.com/api/getvfwebqq', {
                        "ptwebqq": QQ.PTWebQQ,
                        "clientid": QQ.ClientID,
                        "psessionid": QQ.PSessionID,
                },QQ.Referer)
                print u'测试获取vfwebqq:'+str(html)
                QQ.VFWebQQ=json.loads(html)['result']['vfwebqq']
            except:
                pass
            # # TODO 测试
            # try:
            #     print u'测试'
            #     html = self.Get('http://web2.qq.com/web2_cookie_proxy.html')
            #     ret = json.loads(html)
            #     # print u'测试'+str(ret)
            # except:
            #     pass
            # print self.testcookie()

            LoginError = 1
            while LoginError > 0:
                try:
                    html = self.Post('http://d1.web2.qq.com/channel/login2', {
                        'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(
                            QQ.PTWebQQ,
                            QQ.ClientID,
                            QQ.PSessionID)
                    }, QQ.Referer)
                    # html = self.Post('http://d.web2.qq.com/channel/login2', {
                    #     "ptwebqq": QQ.PTWebQQ,
                    #     "clientid": QQ.ClientID, "psessionid": QQ.PSessionID, "status": "online"
                    # })
                    ret = json.loads(html)
                    LoginError = 0
                except:
                    LoginError += 1
                    if LoginError > 100:
                        print u'登录失败次数过多'
                        break
                    print u'登录失败，正在重试'
                    logging.critical(u"登录失败，正在重试")

            if ret['retcode'] != 0:
                raise ValueError, "Login Retcode=" + str(ret['retcode'])
                return

            # QQ.VFWebQQ = ret['result']['vfwebqq']
            QQ.PSessionID = ret['result']['psessionid']

            logging.critical(U"QQ号：{0} 登陆成功, 用户名：{1}".format(ret['result']['uin'], tmpUserName))
            print u"QQ号：{0} 登陆成功, 用户名：{1}".format(ret['result']['uin'], tmpUserName)
            logging.info(u'Login success')
            self.qq = ret['result']['uin']
            QQ.AdminQQ = self.qq
            self.qqname = tmpUserName
            # logging.critical("登陆二维码用时" + pass_time() + "秒")
            QQ.msgId = int(random.uniform(20000000, 50000000))

        def getqq(self):
            return self.qq, self.qqname

    class check_msg(threading.Thread):

        def __init__(self):
            print u'开始监听消息'
            self.wantstop = False
            self.t = QQ.saveMsgThread()
            threading.Thread.__init__(self)

        def run(self):
            # global PTWebQQ
            E = 0
            # 心跳包轮询
            while 1:
                print u'心跳'
                if E > 5:
                    break
                try:
                    ret = self.check()
                except:
                    E += 1
                    continue
                # logging.info(ret)
                print ret
                # 返回数据有误
                if ret == "" or ret['retcode'] == 121:
                    E += 1
                    continue
                # POST数据有误
                if ret['retcode'] == 100006:
                    print u'POST数据有误,结束监听'
                    break

                # 无消息
                if ret['retcode'] == 102:
                    E = 0
                    continue

                # 更新PTWebQQ值
                if ret['retcode'] == 116:
                    QQ.PTWebQQ = ret['p']
                    E = 0
                    continue

                if ret['retcode'] == 0:
                    # 信息分发
                    # msg_handler(ret['result'])
                    if ret.has_key('result'):
                        if str(ret['result'][0]['poll_type']) == 'kick_message':
                            print u'账号在其他地方登录'
                            E = 5
                            continue
                        self.t.save_msg(ret['result'])
                        try:
                            QQ.msg_handler(ret['result'])
                        except Exception, e:
                            print u'回复消息失败:' + str(e)
                        E = 0
                    continue
                if self.wantstop:
                    print u'心跳轮询停止'
                    E = 5
            print u'结束监听'
            logging.critical(u"轮询错误超过五次")

        def stop(self):
            self.wantstop = True

        # 向服务器查询新消息
        def check(self):

            html = QQ.HttpClient_Ist.Post('http://d1.web2.qq.com/channel/poll2', {
                'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(QQ.PSessionID, QQ.PTWebQQ,
                                                                                             QQ.ClientID)
            }, QQ.Referer)
            logging.info(u"Check html: " + str(html))
            try:
                ret = json.loads(html)
            except Exception as e:
                logging.error(str(e))
                logging.critical(u"Check error occured, retrying.")
                return self.check()

            return ret

    class saveMsgThread(threading.Thread):

        def __init__(self):
            self.db_ = mydb()

        def save_msg(self, msgs):
            k = ['msg_id', 'from_uin', 'to_uin', 'info_seq', 'send_uin', 'seq', 'msg_id2', 'time', 'content']
            msg_types = ['message', 'group_message', 'sess_message', 'discu_message']
            param = []
            for msg in msgs:
                keys = msg['value'].keys()
                data = []
                msg_type = msg['poll_type'].encode('utf-8')
                # if msg_type=='message' or msg_type=='group_message' or msg_type=='sess_message' or msg=='discu_message':
                if msg_type in msg_types:
                    data.append(msg_type)
                    value = None
                    for i in k:
                        if i in keys:
                            if i == 'content':  # 内容
                                # TODO 测试下载图片
                                # print msg['value']['to_uin'], QQ.ClientID, QQ.PSessionID, msg['value']['to_uin']
                                value = combine_msg(msg['value']['content'], msg['value']['to_uin'])
                            elif i == 'from_uin':
                                if msg_type == 'message':
                                    from_uin = QQ.uin_to_account(msg['value']['from_uin'])
                                    value = from_uin
                                    print 'trueid:' + str(value)
                                else:
                                    value = msg['value']['from_uin']

                            elif i == 'send_uin':
                                if msg_type == 'group_message' or msg_type == 'discu_message':
                                    send_uin = QQ.uin_to_account(msg['value']['send_uin'])
                                    value = send_uin
                                    print 'trueid:' + str(value)
                                    pass
                                pass
                            else:
                                value = msg['value'][i]
                        else:
                            value = None
                        data.append(value)
                param.append(data)
                # m=(msg_type,msg_id,from_uin,to_uin,info_seq,send_uin,seq,msg_id2,time,content)
            sql = 'INSERT INTO webqq_msg(msg_type,msg_id,from_uin,to_uin,info_seq,send_uin,seq,msg_id2,time,content) VALUES((SELECT id FROM webqq_msgtype WHERE name=%s),%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.db_.exemany(sql, param)

    class pmchat_thread(threading.Thread):
        '''私聊回复线程'''

        def __init__(self, tuin, isSess, group_sig, service_type):
            threading.Thread.__init__(self)
            self.tuin = tuin
            self.isSess = isSess
            self.group_sig = group_sig
            self.service_type = service_type
            self.tqq = QQ.uin_to_account(tuin)
            self.lastcheck = time.time()
            self.lastseq = 0
            self.replystreak = 0
            logging.info("私聊线程生成，私聊对象：" + str(self.tqq))

        def check(self):
            self.lastcheck = time.time()

        def run(self):
            while 1:
                time.sleep(199)
                if time.time() - self.lastcheck > 300:
                    break

        def reply(self, content):
            QQ.send_msg(self.tuin, str(content), self.isSess, self.group_sig, self.service_type)
            logging.info("Reply to " + str(self.tqq) + ":" + str(content))

        def push(self, ipContent, seq):
            if seq == self.lastseq:
                return True
            else:
                self.lastseq = seq
            # 防止机器人对聊
            if self.replystreak > 30:
                self.replystreak = 0
                return True
            try:
                self.replystreak = self.replystreak + 1
                logging.info("PM get info from AI: " + ipContent)
                paraf = {'userid': str(self.tqq), 'key': QQ.tulingkey, 'info': ipContent}
                info = QQ.HttpClient_Ist.Get('http://www.tuling123.com/openapi/api?' + urllib.urlencode(paraf))
                logging.info("AI REPLY:" + str(info))
                info = json.loads(info)
                if info["code"] in [40001, 40003, 40004]:
                    self.reply("我今天累了，不聊了")
                    logging.warning("Reach max AI call")
                elif info["code"] in [40002, 40005, 40006, 40007]:
                    self.reply("我遇到了一点问题，请稍后@我")
                    logging.warning("PM AI return error, code:" + str(info["code"]))
                else:
                    rpy = str(info["text"]).replace('<主人>', '你').replace('<br>', "\n")
                    self.reply(rpy)
                return True
            except Exception, e:
                logging.error("ERROR:" + str(e))
            return False

    class group_thread(threading.Thread):
        last1 = ''
        lastseq = 0
        replyList = {}
        followList = []

        # 属性
        repeatPicture = False

        def __init__(self, guin):
            threading.Thread.__init__(self)
            self.guin = guin
            self.gid = QQ.GroupList[guin]
            self.load()
            self.lastreplytime = 0
            try:
                self.get_group_list()
            except Exception, e:
                print u'错误：' + str(e)

        def get_group_list(self):
            '''获取群列表'''
            print u'获取群列表'
            reqURL = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
            hash = getHashCode(QQ.AdminQQ, QQ.PTWebQQ)
            # data = (
            #     ('r','{"vfwebqq":"{0}","hash":"{1}"}'.format(QQ.VFWebQQ,hash)),
            #     ('vfwebqq',QQ.VFWebQQ),
            #     ('hash',hash)
            # )
            data = {
                'vfwebqq': QQ.VFWebQQ,
                'hash': hash,
            }
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            print u'获取群列表失败:' + str(rsp)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    print u'获取群列表成功:' + str(rspp)
                    gnamelist = rspp['result']['gnamelist']
                    gcode = 0
                    for g in gnamelist:
                        # TODO 保存群信息
                        # TODO 查询每一个群的gcode，然后获取群成员
                        pass
                        #     if g['name'] == u'测试':
                        #         gcode = g['code']
                        # if gcode != 0:
                        #     self.get_group_info(gcode)
            except:
                print u'获取群列表失败:' + str(rsp)
                pass
            return rsp

        def get_group_info(self, gcode):
            print u'获取群成员'
            '''获取群成员'''
            t = time.time()
            reqURL = 'http://s.web2.qq.com/api/get_group_info_ext2'
            data = {
                'gcode': gcode,
                'vfwebqq': QQ.VFWebQQ,
                't': t
            }
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    print u'获取群成员成功:' + str(rspp)
                    # return True
            except:
                print u'获取群成员失败'
                pass
            return rsp

        def learn(self, key, value, needreply=True):
            if key in self.replyList:
                self.replyList[key].append(value)
            else:
                self.replyList[key] = [value]

            if needreply:
                self.reply("我记住" + str(key) + "的回复了")
                self.save()

        def delete(self, key, value, needreply=True):
            if key in self.replyList and self.replyList[key].count(value):
                self.replyList[key].remove(value)
                if needreply:
                    self.reply("我已经不会说" + str(value) + "了")
                    self.save()

            else:
                if needreply:
                    self.reply("没找到你说的那句话哦")

        def reply(self, content):
            if time.time() - self.lastreplytime < 3.0:
                logging.info("REPLY TOO FAST, ABANDON：" + content)
                print u'回复频率表过快'
                return False
            self.lastreplytime = time.time()
            reqURL = "http://d.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r',
                 '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(
                     self.guin, QQ.ClientID, QQ.msgId, QQ.PSessionID,
                     str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
                         "utf-8"))),
                ('clientid', QQ.ClientID),
                ('psessionid', QQ.PSessionID)
            )
            logging.info("Reply package: " + str(data))
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    logging.info("[Reply to group " + str(self.gid) + "]:" + str(content))
                    print "[Reply to group " + str(self.gid) + "]:" + str(content)
                    return True
            except:
                pass
            logging.error("[Fail to reply group " + str(self.gid) + "]:" + str(rsp))
            return rsp

        def handle(self, send_uin, content, seq):
            # 避免重复处理相同信息
            if seq != self.lastseq:
                print u'消息不重复'
                pattern = re.compile(r'^(?:!|！)(learn|delete) {(.+)}{(.+)}')
                match = pattern.match(content)
                if match:
                    print 'match learn'
                    if match.group(1) == 'learn':
                        self.learn(str(match.group(2)).decode('UTF-8'), str(match.group(3)).decode('UTF-8'))
                        logging.debug(self.replyList)
                    if match.group(1) == 'delete':
                        self.delete(str(match.group(2)).decode('UTF-8'), str(match.group(3)).decode('UTF-8'))
                        logging.debug(self.replyList)

                else:
                    # if not self.follow(send_uin, content):
                    #     if not self.tucao(content):
                    #         if not self.repeat(content):
                    #             if not self.callout(content):
                    #                 pass
                    # if self.aboutme(content):
                    #     return
                    # if self.deleteall(content):
                    #     return
                    if self.callout(send_uin, content):
                        return
                        # if self.follow(send_uin, content):
                        #     return
                        # if self.tucao(content):
                        #     return
                        # if self.repeat(content):
                        #     return

            else:
                logging.warning("message seq repeat detected.")
            self.lastseq = seq

        def tucao(self, content):
            for key in self.replyList:
                if str(key) in content and self.replyList[key]:
                    rd = random.randint(0, len(self.replyList[key]) - 1)
                    self.reply(self.replyList[key][rd])
                    logging.info('Group Reply' + str(self.replyList[key][rd]))
                    return True
            return False

        def repeat(self, content):
            if self.last1 == str(content) and content != '' and content != ' ':
                if self.repeatPicture or "[图片]" not in content:
                    self.reply(content)
                    logging.info("已复读：{" + str(content) + "}")
                    return True
            self.last1 = content

            return False

        def follow(self, send_uin, content):
            pattern = re.compile(r'^(?:!|！)(follow|unfollow) (\d+|me)')
            match = pattern.match(content)

            if match:
                target = str(match.group(2))
                if target == 'me':
                    target = str(QQ.uin_to_account(send_uin))

                if match.group(1) == 'follow' and target not in self.followList:
                    self.followList.append(target)
                    self.reply("正在关注" + target)
                    return True
                if match.group(1) == 'unfollow' and target in self.followList:
                    self.followList.remove(target)
                    self.reply("我不关注" + target + "了！")
                    return True
            else:
                if str(QQ.uin_to_account(send_uin)) in self.followList:
                    self.reply(content)
                    return True
            return False

        def save(self):
            try:
                with open("database." + str(self.gid) + ".save", "w+") as savefile:
                    savefile.write(json.dumps(self.replyList))
                    savefile.close()
            except Exception, e:
                logging.error("写存档出错：" + str(e))

        def load(self):
            try:
                with open("database." + str(self.gid) + ".save", "r") as savefile:
                    saves = savefile.read()
                    if saves:
                        self.replyList = json.loads(saves)
                    savefile.close()
            except Exception, e:
                logging.info("读取存档出错:" + str(e))

        def callout(self, send_uin, content):
            print 'callout'
            pattern = re.compile(r'^(@)(robot) (.+)')
            match = pattern.match(content)
            try:
                if match:
                    print 'match:' + str(match.groups())
                    logging.info("get info from AI: " + str(match.group(3)).decode('UTF-8'))
                    print "get info from AI: " + str(match.group(3)).decode('UTF-8')
                    usr = str(QQ.uin_to_account(send_uin))
                    paraf = {'userid': usr + 'g', 'key': QQ.tulingkey, 'info': str(match.group(3)).decode('UTF-8')}

                    info = QQ.HttpClient_Ist.Get('http://www.tuling123.com/openapi/api?' + urllib.urlencode(paraf))
                    logging.info("AI REPLY:" + str(info))
                    info = json.loads(info)
                    if info["code"] in [40001, 40003, 40004]:
                        self.reply("我今天累了，不聊了")
                        logging.warning("Reach max AI call")
                    elif info["code"] in [40002, 40005, 40006, 40007]:
                        self.reply("我遇到了一点问题，请稍后@我")
                        logging.warning("AI return error, code:" + str(info["code"]))
                    else:
                        self.reply(str(info["text"]).replace('<主人>', '你').replace('<br>', "\n"))
                    return True
            except Exception, e:
                logging.error("ERROR" + str(e))
            return False

        def aboutme(self, content):
            pattern = re.compile(r'^(?:!|！)(about)')
            match = pattern.match(content)
            try:
                if match:
                    logging.info("output about info")
                    info = 'about me'
                    self.reply(info)
                    return True
            except Exception, e:
                logging.error("ERROR" + str(e))
            return False

        def deleteall(self, content):
            pattern = re.compile(r'^(?:!|！)(deleteall)')
            match = pattern.match(content)
            try:
                if match:
                    logging.info("Delete all learned data for group:" + str(self.gid))
                    info = "已删除所有学习内容"
                    self.replyList.clear()
                    self.save()
                    self.reply(info)
                    return True
            except Exception, e:
                logging.error("ERROR:" + str(e))
            return False

    class group_check_thread(group_thread):
        '''检查群是否有新成员'''

        def __init__(self, guin, gcode):
            threading.Thread.__init__(self)
            self.member_list = []
            self.guin = guin
            self.gcode = gcode

        def request_member(self, muin):
            if muin not in self.member_list:
                self.member_list.append(muin)

        def run(self):
            e = 0
            while e < 5:
                try:
                    res = self.get_group_info(self.gcode)
                    members = res['result']['ginfo']['members']
                    print u'群成员:' + str(members)
                    print u'申请加入：' + str(self.member_list)
                    for member in members:
                        if member['muin'] in self.member_list:
                            # 删除，并发送消息
                            print u'发送欢迎消息'
                            self.member_list.pop(member['muin'])
                            self.reply('欢迎新成员加入群')
                except:
                    e += 1
                time.sleep(5)
                pass

        def get_group_list(self):
            '''获取群列表'''
            print u'获取群列表'
            reqURL = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
            hash = getHashCode(QQ.AdminQQ, QQ.PTWebQQ)
            data = {
                'vfwebqq': QQ.VFWebQQ,
                'hash': hash,
            }
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            print u'获取群列表失败:' + str(rsp)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    print u'获取群列表成功:' + str(rspp)
                    gnamelist = rspp['result']['gnamelist']
                    gcode = 0
                    for g in gnamelist:
                        if g['name'] == u'测试':
                            gcode = g['code']
                            return gcode
                    if gcode != 0:
                        res = self.get_group_info(gcode)
            except:
                print u'获取群列表失败:' + str(rsp)
                pass
            return False

        def get_group_info(self, gcode):
            print u'获取群成员'
            '''获取群成员'''
            t = time.time()
            reqURL = 'http://s.web2.qq.com/api/get_group_info_ext2'
            data = {
                'gcode': gcode,
                'vfwebqq': QQ.VFWebQQ,
                't': t
            }
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    print u'获取群成员成功:' + str(rspp)
                    # return True
            except:
                print u'获取群成员失败'
                pass
            return rsp

    class discu_thread(group_thread):
        '''讨论组线程'''

        def reply(self, content):
            print u'谈论组回复'
            if time.time() - self.lastreplytime < 3.0:
                logging.info("REPLY TOO FAST, ABANDON：" + content)
                print u'回复频率表过快'
                return False
            self.lastreplytime = time.time()
            reqURL = "http://d.web2.qq.com/channel/send_discu_msg2"
            # data = (
            #     ('r',
            #      '{{"did":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(
            #          self.guin, QQ.ClientID, QQ.msgId, QQ.PSessionID,
            #          str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8"))),
            #     ('clientid', QQ.ClientID),
            #     ('psessionid', QQ.PSessionID)
            # )
            data = {
                'did': self.guin,
                'face': 0,
                'content': '["' + content + '",["font",{"name":"Arial","size":10,"style":[0,0,0],"color":"000000"}]]',
                "clientid": QQ.ClientID,
                "msg_id": QQ.msgId,
                "psessionid": QQ.PSessionID
            }
            logging.info("Reply package: " + str(data))
            rsp = QQ.HttpClient_Ist.Post(reqURL, data, QQ.Referer)
            try:
                rspp = json.loads(rsp)
                if rspp['retcode'] == 0:
                    logging.info("[Reply to group " + str(self.gid) + "]:" + str(content))
                    print "[Reply to group " + str(self.gid) + "]:" + str(content)
                    return True
            except:
                pass
            logging.error("[Fail to reply group " + str(self.gid) + "]:" + str(rsp))
            return rsp
            pass

    # -----------------
    # 主程序
    # -----------------
    # if __name__ == "__main__":
    #
    #     vpath = '../static/img/v.png'
    #     qq = 0
    #     if len(sys.argv) > 1:
    #         vpath = sys.argv[1]
    #     if len(sys.argv) > 2:
    #         qq = sys.argv[2]
    #
    #     try:
    #         pass_time()
    #         qqLogin = Login(vpath, qq)
    #     except Exception, e:
    #         logging.critical(str(e))
    #         os._exit(1)
    #     t_check = check_msg()
    #     t_check.setDaemon(True)
    #     t_check.start()
    #     # try:
    #     #     with open('groupfollow.txt', 'r') as f:
    #     #         for line in f:
    #     #             GroupWatchList += line.strip('\n').split(',')
    #     #         logging.info("关注:" + str(GroupWatchList))
    #     # except Exception, e:
    #     #     logging.error("读取组存档出错:" + str(e))
    #     t_check.join()

    # @classmethod
    def run(self, filename):
        '''运行'''
        # vpath = filename+'.png'
        # vpath = 'static/img/' + filename + '.png'
        vpath = 'static/img/' + filename
        qq = 0
        if len(sys.argv) > 1:
            vpath = sys.argv[1]
        if len(sys.argv) > 2:
            qq = sys.argv[2]
        try:
            QQ.pass_time()
            self.qqLogin = QQ.Login(vpath, qq)
        except Exception, e:
            logging.critical(e)
            # os._exit(1)
            return
        t_check = QQ.check_msg()
        t_check.setDaemon(True)
        t_check.start()
        t_check.join()

    def stop(self):
        self.t_check.stop()
