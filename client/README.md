## Client-Side

##### Mysql Configuration

Here we use docker as mysql container.

1. Create a new image of mysql

```
docker run -p 3306:3306 --name mysql-WLAN -e MYSQL_ROOT_PASSWORD=XXXX -d mysql
```

2. Run the image

```
docker start mysql-WLAN
```



##### Python environment

We use mysql-connector to connect to database in python.

```
pip3 install mysql-connector-python
```

There is a confusing plugin called mysql-connector!!! Don't use that if u use mysql 8.0!



##### Python sql command 

I wrote a template python file *run.py* about how to connect to the database and do common mysql connections.

