#!/bin/sh
export LD_LIBRARY_PATH=/usr/local/mysql/lib/
 
sudo ~/.bash_profile
 
# 需要启用DEBUG模式时将下面三行注释去掉即可
#set -u
#set -x
#set -e
 
BASEDIR="/data/sysbench"    #创建sysbench文件目录
if [ ! -d $BASEDIR ]
then
   sudo mkdir $BASEDIR -p
fi
sudo cd $BASEDIR                 #进入sysbench文件目录
 
# 记录所有错误及标准输出到 sysbench.log 中
#exec 3>&1 4>&2 1>> sysbench_prepare.log 2>&1
 
DBIP="192.168.1.15"
DBPORT=3109
DBUSER='root'
DBPASSWD='ichliebedich11'
NOW=`date +'%Y%m%d%H%M'`
DBNAME="sysbench"
TBLCNT=10           #表数量
WARMUP=300          #预热时间（秒）
DURING=1800         #持续时间（秒）
ROWS=10000000       #每个表中插入1KW行数据
MAXREQ=1000000      #最大请求数为100W
 
#当达到持续时间或者最大请求数时，这一轮的测试就会停止
 
#创建sysbench专用的数据库
echo 'now create db'
mysql -h$DBIP -P$DBPORT -u$DBUSER -p$DBPASSWD -e 'create database sysbench'
echo 'create ok'
## 数据准备
echo 'now prepare data'
 sysbench --test=oltp \    #必须附加lua脚本才可以初始化数据
 --mysql-host=$DBIP \
 --mysql-port=$DBPORT \
 --mysql-user=$DBUSER \
 --mysql-password=$DBPASSWD \
 --mysql-db=$DBNAME \
 --db-driver=mysql \
 --tables=10 \
 --table-size=$ROWS \
 --time=$DURING prepare
