#!/usr/bin/python
#coding=utf-8

import requests
import re
import webbrowser
import threading
import time
import json
from HttpClient import HttpClient
import urllib
import random

url_login = 'http://w.qq.com/login.html'
url_downcode = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=%s' % (time.time()/10**10)
url_checkcode = 'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&'\
'u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&'\
'dumy=&fp=loginerroralert&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10158&login_sig=&'\
'pt_randsalt=0'

ClientID=53999199
PSessionID = ''
Referer = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'

Client = HttpClient()

tulingkey = '6d7bdd3255fb1c940d265f6470b1b641'
FriendList = {}
ThreadList = []
def uin_to_account(tuin):
    # 如果消息的发送者的真实QQ号码不在FriendList中,则自动去取得真实的QQ号码并保存到缓存中
    if tuin not in FriendList:
        try:
            t=int(time.time())*1000
            # print 'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, QQ.VFWebQQ,t)
            info = json.loads(Client.Get(
                'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, VFWebQQ, t),
                Referer))
            # info = json.loads(session.get(
            #     'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(tuin, VFWebQQ, t),
            #     Referer).text)
            print u'真实QQ:' + str(info)
            if info['retcode'] != 0:
                print u'询问真实QQ号出错'
                raise ValueError, info
            info = info['result']
            FriendList[tuin] = info['account']
            print u'获得真实QQ号码：' + str(info['account'])

        except Exception as e:
            print e
    return FriendList[tuin]

def send_msg(tuin, content, isSess, group_sig, service_type):
    '''
    发送消息
    '''
    if isSess == 0:
        reqURL = "http://d1.web2.qq.com/channel/send_buddy_msg2"
        # data = (
        #     ('r',
        #      '{"to":%s, "face":0, "content":"[\\"%s\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"%s", "msg_id":%s, "psessionid":"%s"}'
        #      % (tuin,
        #         str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")),
        #          ClientID, msgId, PSessionID,))
        # )

        data = {
            'r': '{"to":%s, "face":0, "content":\
            "[\\"%s\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\",\
             \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"%s",\
              "msg_id":%s, "psessionid":"%s"}' % ( tuin,
               str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")),
               ClientID,
               msgId,
               PSessionID,),
            'clientid': ClientID,
            'psessionid': PSessionID,

            }
        # rsp = session.post(reqURL, data).text
        _Referer = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        rsp = Client.Post(reqURL, data, _Referer)
        rspp = json.loads(rsp)
        if rspp['retcode'] != 0:
            print u'回复私人消息失败：'+str(rspp)
            # logging.error("reply pmchat error" + str(rspp['retcode']))
    else:
        reqURL = "http://d.web2.qq.com/channel/send_sess_msg2"
        data = (
            ('r',
             '{{"to":{0}, "face":0, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                 tuin, ClientID, msgId, PSessionID,
                 str(content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")),
                 group_sig, service_type)),
            ('clientid', ClientID),
            ('psessionid', PSessionID),
            ('group_sig', group_sig),
            ('service_type', service_type)
        )
        rsp = QQ.HttpClient_Ist.Post(reqURL, data, Referer)
        rspp = json.loads(rsp)
        if rspp['retcode'] != 0:
            print u'回复群消息失败:'+str(rspp)
            # logging.error("reply temp pmchat error" + str(rspp['retcode']))

    return rsp


def thread_exist(tqq):
    for t in ThreadList:
        if t.isAlive():
            if t.tqq == tqq:
                t.check()
                return t
        else:
            ThreadList.remove(t)
    return False

def combine_msg(content, tuin=None):
    '''判断消息'''
    msgTXT = ""
    for part in content:
        if type(part) == type(u'\u0000'):
            msgTXT += part
        elif len(part) > 1:
            # # 如果是图片
            # if str(part[0]) == "offpic" or str(part[0]) == "cface":
            #     if str(part[0]) == 'offpic':
            #         try:
            #             requestOffpic(part[1]['filepath'], tuin)
            #         except:
            #             print u'下载图片失败'
            #     msgTXT += "[图片]"
            # elif str(part[0]) == "face":
            #     index = part[1]
            #     msgTXT += '<img src="/static/img/face/' + str(index) + '.png">'
            pass
    return msgTXT


class pmchat_thread(threading.Thread):
    '''私聊回复线程'''

    def __init__(self, tuin, isSess, group_sig, service_type):
        threading.Thread.__init__(self)
        self.tuin = tuin
        self.isSess = isSess
        self.group_sig = group_sig
        self.service_type = service_type
        self.tqq = uin_to_account(tuin)
        self.lastcheck = time.time()
        self.lastseq = 0
        self.replystreak = 0
        print "私聊线程生成，私聊对象：" + str(self.tqq)

    def check(self):
        self.lastcheck = time.time()

    def run(self):
        while 1:
            time.sleep(199)
            if time.time() - self.lastcheck > 300:
                break

    def reply(self, content):
        send_msg(self.tuin, str(content), self.isSess, self.group_sig, self.service_type)

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
            paraf = {'userid': str(self.tqq), 'key': tulingkey, 'info': ipContent}
            info = Client.Get('http://www.tuling123.com/openapi/api?' + urllib.urlencode(paraf))
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
            print e
        return False


#开始
#登陆
msgId = 0
html = Client.Get(url_login)
# session = requests.Session()
# headers = {
#     'Accept':'application/javascript, */*;q=0.8',
#     'Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
# }
# html = session.get(url_login, headers=headers).text

m = re.findall(r'\.src = "(.+?)"', html)
if m:
    html = Client.Get(m[0])
    # html = session.get(m[0]).text
    APPID = re.findall(r'g_appid\s*=\s*encodeURIComponent\s*\("(\d+)"', html)[0]
    sign = re.findall(r'g_login_sig\s*=\s*encodeURIComponent\s*\("(.+?)"\)', html)[0]
    JsVer = re.findall(r'g_pt_version\s*=\s*encodeURIComponent\s*\("(\d+)"\)', html)[0]
    MiBaoCss = re.findall(r'g_mibao_css\s*=\s*encodeURIComponent\s*\("(.+?)"\)', html)[0]

    startTime = int(time.time())*1000

    Client.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=L&s=8&d=72&v=4', 'test.png')
    # r = session.get('https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=L&s=8&d=72&v=4')
    # output=open('test.png','wb')
    # output.write(r.content)
    # output.close()
    webbrowser.open('test.png')

    #循环验证码
    url_checkcode = url_checkcode + '&action=0-0-%s' % (int(time.time())*1000 - startTime)
    while True:
        time.sleep(5)
        html = Client.Get(url_checkcode)
        # html = session.get(url_checkcode).text
        ret = html.split("'")
        if ret[1] == '65':  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
            break
        if ret[1] == '0':
            print '验证成功'
            break

    # 记录登陆账号的昵称
    tmpUserName = ret[11]

    html = Client.Get(ret[5])

    url = re.findall(r' src="(.+?)"', html)
    if url:
        url = url[0]
        html = Client.Get(url.replace('&amp;', '&'))
        # html = session.get(url.replace('&amp;', '&')).text
        url = re.findall(r'location\.href="(.+?)"', html)[0]
        html = Client.Get(url)
        # html = session.get(url)


    PTWebQQ = Client.getCookie('ptwebqq')
    # PTWebQQ = session.cookies.get('ptwebqq')

    #未知
    html=Client.Post('http://s.web2.qq.com/api/getvfwebqq', {
            "ptwebqq": PTWebQQ,
            "clientid": ClientID,
            "psessionid": PSessionID,
    }, Referer)
    # html = session.post('http://s.web2.qq.com/api/getvfwebqq',
    #              {
    #                 "ptwebqq": PTWebQQ,
    #                 "clientid": ClientID,
    #                 "psessionid": PSessionID,
    #             },
    #          ).text
    VFWebQQ = json.loads(html)['result']['vfwebqq']

    #登陆
    html = Client.Post('http://d1.web2.qq.com/channel/login2', {
        'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(
            PTWebQQ,
            ClientID,
            PSessionID)
    }, Referer)
    # html = session.post('http://d1.web2.qq.com/channel/login2', {
    #     'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(
    #         PTWebQQ,
    #         ClientID,
    #         PSessionID)
    # }).text
    ret = json.loads(html)
    PSessionID = ret['result']['psessionid']
    qq = ret['result']['uin']

    print "QQ号：%s 登陆成功, 用户名：%s" % (ret['result']['uin'], tmpUserName)
    # msgId = int(random.uniform(20000000, 50000000))
    msgId = int(random.uniform(50000000, 80000000))

    #检查消息轮询
    while True:
        html = Client.Post('http://d1.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(PSessionID, PTWebQQ,
                                                                                         ClientID)
        }, Referer)
        # html = session.post('http://d1.web2.qq.com/channel/poll2', {
        #     'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(PSessionID, PTWebQQ,
        #                                                                                  ClientID)
        # }).text
        ret = json.loads(html)
        recode = ret['retcode']
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
            PTWebQQ = ret['p']
            E = 0
            continue

        if ret['retcode'] == 0:
            if ret.has_key('result'):
                #处理消息
                msgs = ret['result']
                for msg in msgs:
                    msgType = msg['poll_type']
                    # QQ私聊消息
                    if msgType == 'message' or msgType == 'sess_message':  # 私聊 or 临时对话
                        txt = combine_msg(msg['value']['content'])
                        tuin = msg['value']['from_uin']#普通消息QQ号加密后
                        msg_id = msg['value']['msg_id']
                        from_account = uin_to_account(tuin)
                        print tuin, txt
                        # print "{0}:{1}".format(from_account, txt)
                        targetThread = thread_exist(from_account)
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
                                    info = json.loads(CLient.Get(
                                        'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                                            myid, tuin, ClientID, PSessionID, service_type, ts), Referer))
                                    # info = json.loads(session.get(
                                    #     'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                                    #         myid, tuin, ClientID, PSessionID, service_type, ts), Referer).text)
                                    if info['retcode'] != 0:
                                        raise ValueError, info
                                    info = info['result']
                                    group_sig = info['value']
                                tmpThread = pmchat_thread(tuin, isSess, group_sig, service_type)
                                tmpThread.start()
                                ThreadList.append(tmpThread)
                                tmpThread.push(txt, msg_id)
                            except Exception, e:
                                print e

        time.sleep(3)
