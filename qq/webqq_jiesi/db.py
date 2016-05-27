# coding=utf-8
from glob import glob

__author__ = 'Administrator'

import MySQLdb, time, logging

import torndb



# import sae.const


class mydb(object):
    def __init__(self, db=None, host=None, port=None, user=None, password=None):
        # self.__MYSQL_DB = sae.const.MYSQL_DB
        # self.__MYSQL_USER = sae.const.MYSQL_USER
        # self.__MYSQL_PASS = sae.const.MYSQL_PASS
        # self.__MYSQL_HOST_M = sae.const.MYSQL_HOST
        # self.__MYSQL_HOST_S = sae.const.MYSQL_HOST_S
        # self.__MYSQL_PORT = int(sae.const.MYSQL_PORT)
        if db == None:
            self.__MYSQL_DB = 'web_test'
        else:
            self.__MYSQL_DB = db
        self.__MYSQL_USER = 'root'
        self.__MYSQL_PASS = 'admin'
        self.__MYSQL_HOST_M = 'localhost'
        self.__MYSQL_PORT = 3306
        self.connect_to_db()

    def __del__(self):
        self.__conn.close()

    def connect_to_db(self):
        try:
            print u'连接数据库'
            # self.__conn = MySQLdb.connect(
            #     host=self.__MYSQL_HOST_M,
            #     port=self.__MYSQL_PORT,
            #     user=self.__MYSQL_USER,
            #     passwd=self.__MYSQL_PASS,
            #     db=self.__MYSQL_DB,
            # )
            self.__MYSQL_HOST_M=self.__MYSQL_HOST_M+':'+str(self.__MYSQL_PORT)
            self.__conn=torndb.Connection(
                host=self.__MYSQL_HOST_M,
                user=self.__MYSQL_USER,
                password=self.__MYSQL_PASS,
                database=self.__MYSQL_DB,
            )
            # self.__cur = self.__conn.
            # self.__conn.execute()
        except Exception, e:
            logging.error(e)
        return True

    def retry(func):
        '''断线重连修饰'''

        def call(self, *args, **kwargs):
            count = 0
            while (count < 5):
                try:
                    return func(self, *args, **kwargs)
                except Exception, e:
                    logging.error(e)
                    if 'MySQL server has gone away' in str(e):
                        self.connect_to_db()
                        count += 1
                    else:
                        count = 5

        return call

    # def reconnect_to_db(self):
    #     count=0
    #     while(count<5):
    #         try:
    #             self.__conn = MySQLdb.connect(
    #                 host=self.__MYSQL_HOST_M,
    #                 port=self.__MYSQL_PORT,
    #                 user=self.__MYSQL_USER,
    #                 passwd=self.__MYSQL_PASS,
    #                 db=self.__MYSQL_DB,
    #             )
    #         except Exception,e:
    #             logging.error(e)
    #             if 'MySQL server has gone away' in str(e):
    #                 count+=1
    #             else:
    #                 count=5
    #     return True





    # cur = conn.cursor()

    @retry
    def checkName(self, name):
        self.__cur.execute('SELECT username FROM users')
        data = self.__cur.fetchall()
        for i in data:
            if name == i[0]:
                return True
        return False

    @retry
    def check(self, name, password=None):
        self.__cur.execute('SELECT * FROM users')
        data = self.__cur.fetchall()
        print data
        if password == None:  # 如果没有密码，查询用户名是否存在
            for i in data:
                if name == i[1]:
                    return True
            return False
        else:  # 密码存在，验证一致性
            for i in data:
                if name == i[1]:
                    if password == i[2]:
                        return True
                    else:
                        return False
            return False
            # finally:
            #     cur.close()
            #     conn.close()

    @retry
    def insert_user(self, name, password):
        regtime = time.ctime()
        sql = 'INSERT  INTO users(username,password,regtime) VALUES("%s","%s","%s")'
        print sql
        self.__cur.execute(sql, (name.encode('utf-8'), password.encode('utf-8'), regtime.encode('utf-8')))
        self.__conn.commit()
        return

    @retry
    def showAllBlogs(self):
        self.__cur.execute('SELECT * FROM blog ORDER BY id DESC ;')  # 倒序得到所有文章
        tem = self.__cur.fetchall()
        return tem

    @retry
    def saveBlog(self, name, title, content):
        '''保存文章到数据库'''
        regtime = time.ctime()
        sql = 'INSERT blog(name,title,blog,time) VALUES("%s","%s","%s","%s")'
        self.__cur.execute(sql.encode('utf-8'), (
            name.encode('utf-8'), title.encode('utf-8'), content.encode('utf-8'), regtime.encode('utf-8')))
        print sql
        self.__conn.commit()
        return

    @retry
    def showAllUsers(self):
        self.__cur.execute('SELECT * FROM users')
        return self.__cur.fetchall()

    @retry
    def showALLChat(self):
        self.__cur.execute('SELECT * FROM chat ORDER BY id DESC')
        return self.__cur.fetchall()

    @retry
    def getTime(self):
        '''获取当前时间'''
        t = time.localtime()
        res = str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec)
        return res

    @retry
    def insertChat(self, name, topic):
        regtime = self.getTime()
        # sql = 'INSERT chat(name,content,time) VALUES("%s","%s","%s")' % (name, topic, regtime)
        # cur.execute(sql.encode('utf-8'))
        sql = 'INSERT chat(name,content,time) VALUES(%s,%s,%s)'
        self.__cur.execute(sql.encode('utf-8'), (name, topic, regtime))
        print sql
        self.__conn.commit()
        return

    @retry
    def showBlog(self, num):
        sql = 'SELECT * FROM blog WHERE id=%s'
        self.__cur.execute(sql, num)
        return self.__cur.fetchone()

    @retry
    def showComment(self, blog_id):
        sql = 'SELECT * FROM comment WHERE blog_id=%s ORDER BY id DESC '
        self.__cur.execute(sql, blog_id)
        return self.__cur.fetchall()

    @retry
    def insertComment(self, blog_id, name, content):
        t = time.ctime()
        sql = 'INSERT comment(blog_id,name,content,time) VALUES(%s,%s,%s,%s)'
        self.__cur.execute(sql.encode('utf-8'),
                           (blog_id, name.encode('utf-8'), content.encode('utf-8'), t.encode('utf-8')))
        self.__conn.commit()
        print sql
        return

    @retry
    def showUserBlog(self, username):
        sql = 'SELECT * FROM blog WHERE name="%s" ORDER BY id DESC '
        self.__cur.execute(sql.encode('utf-8'), username)
        print sql
        return self.__cur.fetchall()

    @retry
    def addClickRate(self, blog_id):
        '''增加一次点击量，并返回数字'''
        sql = 'UPDATE blog SET click_rate=click_rate+1 WHERE id=%s'
        self.__cur.execute(sql, blog_id)
        self.__conn.commit()
        self.__cur.execute('SELECT click_rate FROM blog WHERE id=%s' % blog_id)
        print sql
        return self.__cur.fetchone

    @retry
    def showHotBlog(self, num):
        '''显示最热的文章'''
        sql = 'SELECT * FROM blog ORDER BY click_rate DESC LIMIT %s'
        self.__cur.execute(sql, num)
        return self.__cur.fetchall()

    @retry
    def select(self, sql,values=None):
        print 'select'
        # self.__cur.execute(sql,values)
        # return self.__cur.fetchall()
        if values==None:
            return self.__conn.query(sql)
        else:
            return self.__conn.query(sql,values)

    @retry
    def insert(self, sql, values):
        print u'插入:'
        # self.__cur.execute(sql, values)
        # self.__conn.commit()
        self.__conn.execute(sql,values)

    @retry
    def exemany(self,sql,param):
        # self.__cur.execute
        print u'executemany'
        self.__conn.executemany(sql,parameters=param)
