-- coding=utf-8
-- To create the database:
--   CREATE DATABASE blog;
--   GRANT ALL PRIVILEGES ON blog.* TO 'blog'@'localhost' IDENTIFIED BY 'blog';
-- To reload the tables:
--   mysql --user=blog --password=blog --database=blog < schema.sql
-- mysql --user=root --password=13961000804 --database=web_test < schema.sql


SET SESSION storage_engine='InnoDB';
ALTER DATABASE CHARACTER SET 'utf8';





DROP TABLE IF EXISTS webqq_msg;
DROP TABLE IF EXISTS webqq_msgtype;
DROP TABLE IF EXISTS webqq_qqlist;

CREATE TABLE webqq_msgtype(
  id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(15) NOT NULL,
  KEY `idx_webqq_msgtype`(`name`)
);

INSERT INTO webqq_msgtype(name) VALUES('message');
INSERT INTO webqq_msgtype(name) VALUES('group_message');
INSERT INTO webqq_msgtype(name) VALUES('input_notify');
INSERT INTO webqq_msgtype(name) VALUES('sess_message');
INSERT INTO webqq_msgtype(name) VALUES('discu_message');


CREATE TABLE webqq_msg(
  id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  msg_type SMALLINT UNSIGNED COMMENT '消息类型',
  msg_id INT UNSIGNED COMMENT '消息id',
  from_uin INT UNSIGNED COMMENT '普通消息QQ号',
  to_uin INT UNSIGNED COMMENT '接受消息的QQ号',
  info_seq INT UNSIGNED COMMENT '群号',
  send_uin INT UNSIGNED COMMENT '群消息发送人QQ号',
  seq INT UNSIGNED COMMENT '未知',
  msg_id2 INT UNSIGNED COMMENT '消息id2',
  time INT UNSIGNED COMMENT '发送时间',
  content TEXT COMMENT '消息内容',
  key `idx_webqq_to_uin`(`to_uin`),
  key `idx_webqq_info_seq`(`info_seq`),
  key `idx_webqq_send_uin`(`send_uin`),
  KEY `idx_webqq_time`(`time`),
  FOREIGN KEY(msg_type) REFERENCES webqq_msgtype(id)
);

CREATE TABLE webqq_qqlist(
  user_id SMALLINT UNSIGNED KEY ,
  qqnum INT NOT NULL,
  qqname VARCHAR(30),
  status TINYINT COMMENT "0掉线，1在线"
);
