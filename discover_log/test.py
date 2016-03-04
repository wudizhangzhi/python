#coding=utf8
import sqlite3

db = sqlite3.connect('loginfo.db')
cur = db.cursor()
data = ['/var/log/auth.log.4.gz','/var/log/lastlog','/var/log/pm-powersave.log.2.gz','/var/log/auth.log.3.gz', '/var/log/alternatives.log.3.gz', '/var/log/mysql.log.5.gz', '/var/log/mysql.log.4.gz', '/var/log/dpkg.log.2.gz', '/var/log/fontconfig.log', '/var/log/btmp.1', '/var/log/syslog', '/var/log/vsftpd.log', '/var/log/mysql.log.1.gz', '/var/log/apport.log.2.gz', '/var/log/alternatives.log.1', '/var/log/syslog.3.gz', '/var/log/udev', '/var/log/auth.log.1', '/var/log/alternatives.log', '/var/log/mysql.log.6.gz', '/var/log/dmesg.1.gz', '/var/log/mysql.err', '/var/log/gpu-manager.log', '/var/log/kern.log.3.gz', '/var/log/dmesg.3.gz', '/var/log/dmesg.0', '/var/log/bootstrap.log', '/var/log/dpkg.log.3.gz', '/var/log/pm-suspend.log.1', '/var/log/syslog.7.gz', '/var/log/pm-suspend.log', '/var/log/kern.log.1', '/var/log/auth.log', '/var/log/boot.log', '/var/log/mysql.log.2.gz', '/var/log/wtmp.1', '/var/log/syslog.6.gz', '/var/log/syslog.5.gz', '/var/log/dpkg.log', '/var/log/dpkg.log.1', '/var/log/yum.log', '/var/log/pm-powersave.log.1', '/var/log/mysql.log.3.gz', '/var/log/kern.log.4.gz', '/var/log/dmesg.4.gz', '/var/log/auth.log.2.gz', '/var/log/Xorg.1.log', '/var/log/alternatives.log.2.gz', '/var/log/dmesg', '/var/log/dmesg.2.gz', '/var/log/kern.log.2.gz', '/var/log/btmp', '/var/log/pm-powersave.log.3.gz', '/var/log/pm-powersave.log', '/var/log/mysql.log', '/var/log/kern.log', '/var/log/syslog.4.gz', '/var/log/wtmp', '/var/log/apport.log', '/var/log/Xorg.0.log', '/var/log/apport.log.3.gz', '/var/log/faillog', '/var/log/syslog.2.gz', '/var/log/syslog.1', '/var/log/mysql.log.7.gz', '/var/log/Xorg.0.log.old', '/var/log/pm-suspend.log.2.gz', '/var/log/apport.log.1']
r = []
# for i in data:
#     t.append()
# print t
for i in data:
    t = []
    t.append(i)
    r.append(t)

# cur.executemany('insert into log_select values(?)',r)
cur.execute('select * from log_select')
# cur.execute('select * from sqlite_master where type="table" and name="log_select";')
print cur.fetchall()
cur.close()
db.close()


data = [(u'/var/log/auth.log.4.gz',), (u'/var/log/lastlog',), (u'/var/log/pm-powersave.log.2.gz',), (u'/var/log/auth.log.3.gz',), (u'/var/log/alternatives.log.3.gz',), (u'/var/log/mysql.log.5.gz',), (u'/var/log/mysql.log.4.gz',), (u'/var/log/dpkg.log.2.gz',), (u'/var/log/fontconfig.log',), (u'/var/log/btmp.1',), (u'/var/log/syslog',), (u'/var/log/vsftpd.log',), (u'/var/log/mysql.log.1.gz',), (u'/var/log/apport.log.2.gz',), (u'/var/log/alternatives.log.1',), (u'/var/log/syslog.3.gz',), (u'/var/log/udev',), (u'/var/log/auth.log.1',), (u'/var/log/alternatives.log',), (u'/var/log/mysql.log.6.gz',), (u'/var/log/dmesg.1.gz',), (u'/var/log/mysql.err',), (u'/var/log/gpu-manager.log',), (u'/var/log/kern.log.3.gz',), (u'/var/log/dmesg.3.gz',), (u'/var/log/dmesg.0',), (u'/var/log/bootstrap.log',), (u'/var/log/dpkg.log.3.gz',), (u'/var/log/pm-suspend.log.1',), (u'/var/log/syslog.7.gz',), (u'/var/log/pm-suspend.log',), (u'/var/log/kern.log.1',), (u'/var/log/auth.log',), (u'/var/log/boot.log',), (u'/var/log/mysql.log.2.gz',), (u'/var/log/wtmp.1',), (u'/var/log/syslog.6.gz',), (u'/var/log/syslog.5.gz',), (u'/var/log/dpkg.log',), (u'/var/log/dpkg.log.1',), (u'/var/log/yum.log',), (u'/var/log/pm-powersave.log.1',), (u'/var/log/mysql.log.3.gz',), (u'/var/log/kern.log.4.gz',), (u'/var/log/dmesg.4.gz',), (u'/var/log/auth.log.2.gz',), (u'/var/log/Xorg.1.log',), (u'/var/log/alternatives.log.2.gz',), (u'/var/log/dmesg',), (u'/var/log/dmesg.2.gz',), (u'/var/log/kern.log.2.gz',), (u'/var/log/btmp',), (u'/var/log/pm-powersave.log.3.gz',), (u'/var/log/pm-powersave.log',), (u'/var/log/mysql.log',), (u'/var/log/kern.log',), (u'/var/log/syslog.4.gz',), (u'/var/log/wtmp',), (u'/var/log/apport.log',), (u'/var/log/Xorg.0.log',), (u'/var/log/apport.log.3.gz',), (u'/var/log/faillog',), (u'/var/log/syslog.2.gz',), (u'/var/log/syslog.1',), (u'/var/log/mysql.log.7.gz',), (u'/var/log/Xorg.0.log.old',), (u'/var/log/pm-suspend.log.2.gz',), (u'/var/log/apport.log.1',)]

print data[0][0]