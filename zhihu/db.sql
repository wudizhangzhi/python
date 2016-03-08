drop table if exists `zhihu_question`;
create table `zhihu_question`(
    `id` int unsigned primary key auto_increment,
    `question_id` int unsigned not null,
    `title` varchar(153) not null comment'题目',
    `content` text comment'问题正文',
    `time` int not null comment'记录时间',
    `time_recent` int comment'最近活动时间',
    `num_answer` tinyint comment'回答数量',
    `num_follow` int comment'关注人数',
    `num_watch` int comment'浏览人数',
    key `idx_qestion_id` (`question_id`) 
);

drop table if exists `zhihu_answer`;
create table `zhihu_answer`(
    `id` int unsigned primary key auto_increment,
    `question_id` int unsigned not null,
    `primary` text comment'概述',
    `agree` int comment'赞同数量',
    `content` longtext comment'回答',
    `time` int comment'编辑时间'
);

drop table if exists `zhihu_user`;
create table `zhihu_user`(
    `id` int unsigned primary key auto_increment,
    `name` varchar(52) comment'用户名',
    `sign` varchar(150) comment'一句话概括',
    `avatar` text comment'url',
    `location` varchar(30) comment'居住地',
    `business` varchar(30) comment'行业',
    `gender` int comment'性别0:女，1:男',
    `employment` varchar(60) comment'职业',
    `education` varchar(60) comment'教育',
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
    `watched` int default 0 comment'主页被查看次数'

);
