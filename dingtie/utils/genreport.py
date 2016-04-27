#/usr/bin/python
# -*- coding: utf-8 -*-

#from collections import OrderedDict
#from pyexcel_xls import save_data
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import torndb
import redis
import time
import json
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
try:
    fp = file('config/config.ini')
    config_data = fp.read()
    fp.close()

    config_json = json.loads(config_data)['config']

    redis_host = config_json['redis_host']
    redis_port = config_json['redis_port']
    mysql_host = config_json['mysql_host']
    mysql_db = config_json['mysql_db']
    mysql_user = config_json['mysql_user']
    mysql_pass = config_json['mysql_pass']

    pre_system = config_json['pre_system']
    serverport = config_json['http_port']
except Exception, ex:
    print ex
    sys.exit(-1)

# 链接redis
pool = redis.ConnectionPool(host=redis_host, port=redis_port)
redis_cursor = redis.Redis(connection_pool=pool)

# 链接mysql
mysql_cursor = torndb.Connection(mysql_host, mysql_db, user=mysql_user,
                                 password=mysql_pass)




title = [u'序号',u'单位',u'舆情事件名称', u'发帖网站', u'新闻标题', u'新闻发布时间', u'发帖时间所在位置', u'贴文URL链接', u'发帖时间', u'发帖昵称', u'引导信息内容', u'突出亮点说明', u'截图']

def createExcel(datas, filename):
    length_key = len(title)
    length_data = len(datas)
    filename = '%s.xlsx' % filename
    filepath = os.path.dirname(filename)
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    # 表格格式
    format = workbook.add_format()
    format.set_border(1) # 边框
    format.set_align('center')
    format.set_align('vcenter')
    format.set_text_wrap()
    # 格式应用到每一列
    worksheet.set_column(0, 0, 5, format)
    worksheet.set_column(1, 1, 10, format)
    worksheet.set_column(2, length_key-1, 20, format)

    # 第一行标题
    for i in range(len(title)):
        worksheet.write(0, i, title[i])
    row = 1
    col = 1

    # Iterate over the data and write it out row by row.
    for data in datas:
        worksheet.set_row(row, 30)

        #数据个数不匹配
        if len(data) != (len(title)-2):
            return False
        for j in range((len(title))):
            if j == 0:# 第一列序号
                worksheet.write(row, j, row)
            elif j == 1:# 第二列江苏
                worksheet.write(row, j, u'江苏')
            elif j == (len(title) -1):
                if data[j-2] != '':
                    # worksheet.insert_image(row, j, data[j-2], {'x_scale': 0.01, 'y_scale': 0.008, 'x_offset': 80, 'y_offset': 10 , 'positioning': 1})
                    worksheet.insert_image(row, j, data[j-2], {'x_scale': 0.17, 'y_scale': 0.012, 'x_offset': 25, 'y_offset': 5, 'positioning': 1})
            elif j == length_key-2:
                count, floor = data[j-2].split(',')
                worksheet.write(row, j, '引导评论贴文获%s次支持并处于新闻热评栏第%s位' % (count, floor))
            else:
                worksheet.write_string(row, j, data[j-2])
        row += 1

    workbook.close()
    return True


'''
生成热门回帖截图
url:      网页地址
url_type: 网页类型
filename: 保存截图名称,不需要后缀名
page:页码
'''
def OutPutImg(postid, url_type, filename,page=1):
    print '开始截图: %s' % postid
    filepath = '../static/excel/imgs/'
    # filepath = ''
    sql = 'select list.url as url from system_url_posts as post, system_url_list as list where post.postid=%s and post.urlid=list.urlid;'
    ret = mysql_cursor.query(sql, postid)
    if ret:
        url = ret[0]['url']
    else:
        return False

    if not os.path.exists(filepath):
        os.mkdir(filepath)
    driver = webdriver.PhantomJS()
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    driver.get(url)

    # 跳页
    if page != 1:
        wait = WebDriverWait(driver, 10)
        if url_type == '163':
            element = wait.until(EC.presence_of_element_located((By.ID,'tie-data-2')))
            pagebutton = driver.find_element_by_xpath('//ul[@class="hot-pages"]/li[%s]/a' % (page+1))
            pagebutton.click()
            element = wait.until(EC.presence_of_element_located((By.ID,'tie-data-2')))
        elif url_type == 'ifeng':
            pass
        else:
            return False



    driver.save_screenshot(filepath + 'fullscreen_%s.png' % filename)
    # 不同门户选取的位置不同
    if url_type == '163':
        imgelement = driver.find_element_by_xpath('//div[@class="wrapper origPost"]')
        location_title = imgelement.location
        size_title = imgelement.size
        imgelement = driver.find_element_by_xpath('//div[@id="hotReplies"]')
        location_hot = imgelement.location
        size_hot = imgelement.size

        rangle = (int(location_title['x']), int(location_title['y']), int(location_title['x']) + \
            size_hot['width'], int(location_title['y']) + size_title['height'] + size_hot['height'] + 50)

    elif url_type == 'ifeng':
        
        imgelement = driver.find_element_by_xpath('//div[@class="i-mainContent"]')
        location_main = imgelement.location

        imgelement = driver.find_element_by_xpath('//div[@class="js_hotCmtBlock"]')
        location_hot = imgelement.location
        size = imgelement.size

        rangle = (int(location_main['x']) - 10, int(location_main['y']), int(location_main['x']) + size['width'] + 20, int(location_main['y']) + size['height'] + 350)

    else:
        return False
    # location = imgelement.location
    # size = imgelement.size
    # rangle = (int(location['x']),int(location['y']),int(location['x']+size['width']),int(location['y'])+size['height'])

    i = Image.open(filepath + 'fullscreen_%s.png' % filename)

    # size = i.size
    # rangle = (0, 0, size[0], size[1]*2/5)

    # rangle = (0, 0, size['width'], size['height']/3)

    frame4 = i.crop(rangle)
    frame4.resize((660, 2600)).save(filepath + str(filename) + '.jpg')
    # frame4.save(filepath + str(filename) + '.jpg')
    sql = 'update system_url_posts set screenshot=%s where postid=%s'
    mysql_cursor.execute(sql, ('static/excel/imgs/' + filename + '.jpg'), filename)
    print '结束截图: %s' % postid
    return True





if __name__ == '__main__':
    import time
    t = time.time()
    # url = 'http://gentie.ifeng.com/view.html?docUrl=http%3A%2F%2Fnews.ifeng.com%2Fa%2F20160412%2F48430447_0.shtml&docName=%E8%B6%8A%E5%8D%97%E8%8B%8F30%E6%88%98%E6%9C%BA%E9%A3%9E%E8%B6%8A%E4%B8%AD%E5%9B%BD%E5%8D%97%E5%A8%81%E5%B2%9B%E7%94%BB%E9%9D%A2%E6%9B%9D%E5%85%89%28%E5%9B%BE%29&skey=2b4182'
    # OutPutImg(122, 'ifeng', 'test',page=1)
    # OutPutImg(100, 'ifeng', '175', page=1)
    OutPutImg(146, '163', '173',page=1)
    print '截图完成：%s' % (time.time()-t)

