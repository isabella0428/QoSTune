import mysql.connector
 
mydb = mysql.connector.connect(
           host="47.96.140.67",       # 数据库主机地址
             user="root",    # 数据库用户名
               passwd="8888"   # 数据库密码
               )
  
print(mydb)

mycursor = mydb.cursor()
mycursor.execute("SHOW DATABASES")
   
for x in mycursor:
    print(x)
