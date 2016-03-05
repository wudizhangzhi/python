#coding=utf8
import sqlite3

db = sqlite3.connect('loginfo.db')
cur = db.cursor()
cur.execute('insert into log_select values("fuck u")')
# cur.executemany('insert into log_select values(?)',r)
cur.execute('select * from log_select')
# cur.execute('select * from sqlite_master where type="table" and name="log_select";')
print cur.fetchall()
cur.close()
db.close()



