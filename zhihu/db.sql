drop table if exists `zhihu_question`;
create table `zhihu_question`(
    `id` int unsigned primary key auto_increment,
    `question_id` int unsigned not null,
    `title` varchar(153) not null comment'题目',
    `content` text comment'问题正文',
    `time` int not null comment'记录时间',
    `time_recent` int comment'最近活动时间',
    `num_answer` int comment'回答数量',
    `num_follow` int comment'关注人数',
    `num_watch` int default null comment'浏览人数',
    key `idx_qestion_id` (`question_id`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists `zhihu_answer`;
create table `zhihu_answer`(
    `id` int unsigned primary key auto_increment,
    `token` int unsigned not null,
    `question_id` int unsigned not null,
    `username` varchar(52) not null comment'用户名',
    `time` int unsigned not null comment'最后编辑时间',
    `content` longtext comment'回答',
    key `idx_token` (`token`),
    key `idx_question_id` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists `zhihu_answer_data`;
create table `zhihu_answer_data`(
    `id` int unsigned primary key auto_increment,
    `token` int unsigned not null,
    `agree` int comment'赞同数量',
    `content` longtext comment'回答',
    `num_comment`int comment'评论数量',
    `time` int comment'采集时间'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


drop table if exists `zhihu_user`;
create table `zhihu_user`(
    `id` int unsigned primary key auto_increment,
    `urlname` varchar(52) comment'用户url地址标识',
    `name` varchar(52) comment'用户名',
    `sign` varchar(150) comment'一句话概括',
    `avatar` text comment'头像地址',
    `location` varchar(30) comment'居住地',
    `business` varchar(30) comment'行业',
    `gender` int comment'性别0:女，1:男,2:未知',
    `employment` varchar(60) comment'职业',
    `education` varchar(60) comment'教育'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists `zhihu_user_data`;
create table `zhihu_user_data`(
    `id` int unsigned primary key auto_increment,
    `urlname` varchar(52) comment'用户url地址标识',
    `agree` int default 0 comment'赞同',
    `thanks` int default 0 comment'感谢',
    `fav` int default 0 comment'被收藏',
    `share` int default 0 comment'分享',
    `asks` int default 0 comment'提问',
    `answers` int default 0 comment'回答',
    `posts` int default 0 comment'专栏文章',
    `collections` int default 0 comment'收藏',
    `logs` int default 0 comment'公共编辑',
    `followees` int default 0 comment'关注了',
    `followers` int default 0 comment'被关注',
    `watched` int default 0 comment'主页被查看次数',
     key `idx_urlname` (`urlname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


drop table if exists `zhihu_url_crawled`;
create table `zhihu_url_crawled`(
    `id` int unsigned primary key auto_increment,
    `url` varchar(102) comment'url地址',
     key `idx_url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;