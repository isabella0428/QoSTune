# ECS of Ali Cloud

```
ssh root@ip
```

## Install MySQL server (ver 14.14)

```
sudo apt-get update
sudo apt-get install mysql-server
```

The password of the root administrator is :

8888

```
sudo apt-get install mysql-client
```

Then, credits: https://blog.csdn.net/u014710843/article/details/80276035

```
mysql -uroot -p
vim /etc/mysql/mysql.conf.d/mysqld.cnf
```

comment 'bind-address = 127.0.0.1'

```
service mysql restart
mysql -uroot -p
show databases;
use mysql;
update user set host='%' where user='root' and host='localhost'; #将host设置为%表示任何ip都能连接mysql，当然您也可以将host指定为某个ip
flush privileges;        #刷新权限表，使配置生效
```

Then on Ali Cloud, add 安全组



使用Navicat客户端 ssh 方式可以远程访问MySQL

## Install MySQL python connector:

### Install python3-pip

```
apt install python3-pip
```

### Install mysql-connector

```
python3 -m pip install mysql-connector
```

Oops!

```
Traceback (most recent call last):
  File "/usr/lib/python3.5/runpy.py", line 184, in _run_module_as_main
    "__main__", mod_spec)
  File "/usr/lib/python3.5/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/usr/lib/python3/dist-packages/pip/__main__.py", line 19, in <module>
    sys.exit(pip.main())
  File "/usr/lib/python3/dist-packages/pip/__init__.py", line 215, in main
    locale.setlocale(locale.LC_ALL, '')
  File "/usr/lib/python3.5/locale.py", line 594, in setlocale
    return _setlocale(category, locale)
locale.Error: unsupported locale setting
```

Credits: https://stackoverflow.com/questions/36394101/pip-install-locale-error-unsupported-locale-setting?rq=1

```
export LC_ALL=C
```

Then I use:

```
pip3 install mysql-connector-python
```

Bingo! 

And the version of pip3 is out of date, so I use order below to upgrade it:

```
pip3 install --upgrade pip
```

Then I use python3, 

```
import mysql.connector
```

no warning nor error, so succeed.

