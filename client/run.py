# Author:   Yi Lyu
# Data:     2020.05.05
# This file is a template file for connecting the database using python
#   And execute common sql operations

import mysql.connector

if __name__ == "__main__":
    # Establish connection
    mydb = mysql.connector.connect(
        host="localhost",      
        user="root",    
        passwd="ichliebedich11",  
        auth_plugin='mysql_native_password',
        database="trial"
    )

    cursor = mydb.cursor()

    # Create a database(Only once)
    # cursor.execute("create database trial")

    # Create a table
    cursor.execute("drop table if exists student")
    cursor.execute("create table student (name varchar(10), id int)")

    # Insert a record
    sql = "insert into student(name, id) values(%s, %s)"
    val = [
        ("Sizhe Wei", "1"),
        ("Yi Lyu", "2")
    ]
    cursor.executemany(sql, val)

    # elect the inserted record
    sql = "select * from student"
    cursor.execute(sql)

    myresult = cursor.fetchall()
    for res in myresult:
        print(res)
