import mysql.connector
import numpy as np
import pickle
import time
import os

class Env:
    def __init__(self, variables=None, metrics="QPS", hostname="47.96.140.67", username="root", password="8888"):
        self.variables = variables                              # Knobs to set
        self.metrics = metrics                                  # Metrics for evaluating performance
        self.mydb = self.login(hostname, username, password)
        self.cursor = self.mydb.cursor()
        self.sysbench_clean()
        # self.sysbench_prepare()
    
    def saveDefaultSetting(self):
        """
        Store default global setting
        """
        command = "show global variables;"
        
        defaultSetting = {}
        result = self.getValue(command)
        for line in result:
            defaultSetting[line[0]] = line[1]
        
        with open("data/defaultSetting.pkl", "wb") as output:
            pickle.dump(defaultSetting, output, pickle.HIGHEST_PROTOCOL)
        
    def getDefaultSetting(self):
        """
        Read default global setting
        """
        with open("data/defaultSetting.pkl", "rb") as output:
            data = pickle.load(output)
        return data

    def login(self, hostname, username, password):
        """
        Login to Alibaba remote server
        """
        mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=password,
        )
        return mydb
    
    def execute(self, query):
        """
        Update, Insert, Delete commands
        """
        self.cursor.execute(query)
    
    def getValue(self, query):
        """
        Get commands
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def getQueryVec(self, queries, dim=[1, 100]):
        """
        Generate vector from query
        """
        vec = np.zeros(dim)
        # TODO: Get feature from execution plan
        for query in queries:
            vec += vec
        return vec
    
    def getMetricsVec(self):
        """
        Generate vector from metrics
        """
        if self.metrics == "QPS":   # Query per second
            command = "show global status where Variable_name in ('com_select','com_insert','com_delete','com_update');"

            preValue = self.getValue(command)        # Select, insert, delete and update queries number
            time.sleep(5)                            # Wait 5 seconds
            nextValue = self.getValue(command)
            return nextValue - preValue
    
    def getState(self):
        """
        Concatenate queryVector, metricsVector as state vector
        """
        queryVec = self.getQueryVec()
        metricsVec = self.getMetricsVec()

        totalVec = []
        totalVec.append(queryVec)
        totalVec.append(metricsVec)
        return totalVec
    
    def reset(self):
        """
        Drop all tables
        """
        command = "show tables"
        result = self.execute(command)

        for table in result:
            command = "drop table " + table + ";"
            self.execute(command)
        return
    
    def sysbench_prepare(self):
        command = "sysbench --test=oltp --mysql-table-engine=innodb --oltp-table-size=1000000 --mysql-host=47.96.140.67 --mysql-user=root --mysql-password=8888 --mysql-socket=/var/lib/mysql/mysql.sock  prepare"
        os.system(command)

    def sysbench_test(self):
        command = "sysbench --test=oltp --mysql-table-engine=innodb --oltp-table-size=1000000 --mysql-host=47.96.140.67 --mysql-user=root --mysql-password=8888 --mysql-socket=/var/lib/mysql/mysql.sock --max-time=3 run > test.txt"
        #os.system(command)

        f = open("test.txt", "r")
        lines = f.readlines()
    
        avg_request_time = 0

        for line in lines:
            line = line.strip()
            items = line.split(" ")
            for item in items:
                if item == "avg:":
                    avg_request_time = items[-1]
                    break
        
        
        avg_request_time = float(avg_request_time.split("ms")[0])
        print(avg_request_time)

    def sysbench_clean(self):
        command="./sysbench --test=oltp --num-threads=5 cleanup"
        os.system(command)

    def close(self):
        self.cursor.close()
        self.mydb.close()
