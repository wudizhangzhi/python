#!/usr/bin/python
#coding=utf-8


from bs4 import BeautifulSoup
import requests

def search():
    '''
    小根根程序
    '''
    nums = []

    try:
        with open('data.txt', 'r') as f:
            nums = f.readlines()
    except Exception,e:
        print '请在当前目录创建文件:data.txt,并每行写入一个卡号'
        return


    if len(nums) == 0:
        print '请在当前目录创建文件:data.txt,并每行写入一个卡号'

    headers = {
            'Host':"www.yintongcard.com",
            'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer':"https://www.yintongcard.com/ics-mallweb/CardService.do?_locale=zh_CN&BankId=999999999999&LoginType=C"
            }


    session = requests.Session()
    url = 'https://www.yintongcard.com/ics-mallweb/CardService.do?_locale=zh_CN&BankId=999999999999&LoginType=C'
    session.get(url)

    headers = {
            'Host':"www.yintongcard.com",
            'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
            'Referer':"https://www.yintongcard.com/ics-mallweb/QuickMemberAcNoBalQryPre.do?BankId=999999999999",
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',

            }


    url = 'https://www.yintongcard.com/ics-mallweb/QuickMemberAcNoBalQryPre.do?BankId=999999999999'
    session.get(url, headers=headers)






    url = 'https://www.yintongcard.com/ics-mallweb/QuickMemberAcNoBalQry.do'

    headers = {
            'Host':"www.yintongcard.com",
            'Referer':"https://www.yintongcard.com/ics-mallweb/QuickMemberAcNoBalQryPre.do?BankId=999999999999",
            'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
            'Referer':"https://www.yintongcard.com/ics-mallweb/QuickMemberAcNoBalQryPre.do?BankId=999999999999",
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            }

    with open('result.txt', 'w') as f:
        for num in nums:

            data = {
                        'AcNo':str(num).strip()
                        }


            r = session.post(url, data=data, headers=headers)
            # print r.text
            soup = BeautifulSoup(r.text, "lxml")
            results = soup.find_all('td', class_='td_vlue')
            if len(results) > 1:
                # print '卡号：%s, 余额：%s' % (str(results[0].get_text().strip()), str(results[1].get_text().strip()))
                content = '卡号：%s, 余额：%s' % (str(results[0].get_text().strip()), str(results[1].get_text().strip()))
            else:
                # print '未查到结果：%s' % num
                content = '未查到结果：%s' % num
            print content
            f.write(content + '\n')


if __name__ == '__main__':
    search()
