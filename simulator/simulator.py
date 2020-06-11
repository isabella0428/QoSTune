import mysql.connector
import numpy as np
import pickle
import datetime, time
import os
import random
import re

class Env:
    def __init__(self, unit, variables=None, metrics="QPS"):
        self.variables = variables                              # Knobs to set
        self.metrics = metrics                                  # Metrics for evaluating performance
        self.mydb = self.login()
        self.cursor = self.mydb.cursor()
        self.defaultSetting = self.getDefaultSetting()
        self.queries = ""
        self.defaultWordload, self.queryVec = self.generateQuery()
        self.unit = unit
    
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

    def login(self, hostname="47.96.140.67", username="root", password="8888"):
        """
        Login to Alibaba remote server
        """
        mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=password,
            autocommit=1
        )
        return mydb
    
    def execute(self, query):
        """
        Update, Insert, Delete commands
        """
        self.cursor.execute(query, multi=True)
    
    def executeAction(self, action):
        command = "set session {}={};"               # 8KB * n
        selectCom = "show session variables like '{}';"
        prevVal = self.currentKnobValue()
        newVal = [0] * len(self.variables)
        for i, var in enumerate(self.variables):
            act = int(action[i])
            com = command.format(var, act * self.unit[i])
            self.mydb.cmd_query(com)
        temp = "Previous is {}, now is {}"
        # print(temp.format(prevVal,  self.currentKnobValue()))
    
    def getValue(self, query):
        """
        Get commands
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result
   
    # TODO: change count of queries
    def generateQuery(self, maxVal=1000):
        maxComVal = 1000000
        insert = random.randint(1, maxComVal)
        delete = random.randint(1, maxComVal)
        update = random.randint(1, maxComVal)
        select = random.randint(1, maxComVal)

        commands = ""
        commands += "use test1;"
        insertCommand = "insert into happy values({});"
        updateCommand = "update happy set id={} where id={};"
        selectCommand = "select * from happy where id={};"
        deleteCommand = "delete from happy where id={}"

        inserted = set()
        for i in range(insert):
            value = random.randint(1, maxVal)
            if value in inserted:
                continue
            com = insertCommand.format(value)
            commands += com
            inserted.add(value)

        for i in range(update):
            oldValue = random.randint(1, maxVal)
            if oldValue not in inserted:
                continue
            newValue = random.randint(1, maxVal)
            com = updateCommand.format(oldValue, newValue)
            commands += com
        
        for i in range(select):
            value = random.randint(1, maxVal)
            com = selectCommand.format(value)
            commands += com
        
        for i in range(delete):
            oldValue = random.randint(1, maxVal)
            if oldValue not in inserted:
                continue
            com = deleteCommand.format(oldValue)
            commands += com

        self.queries = commands
        return commands, [insert, delete, update, select]

    def getAllMetrics(self, queries):
        string1 = 'test1'
        self.cursor.execute(queries, multi=True)
        com = "show session variables;"
        result = self.getValue(com)

        metrics = {}
        for res in result:
            if re.match(r'^[0-9]+$', res[1]):
                metrics[res[0]] = int(res[1])
        return metrics

    def getDefaultSettingExecuteTime(self, queries):
        prevSetting = self.currentKnobValue()
        command = "set session {}={};"
        for var in self.variables:
            defaultVal = self.defaultSetting[var]
            com = command.format(var, defaultVal)
            self.mydb.cmd_query(com)
        
        startTime = time.time()
        self.cursor.execute(queries, multi=True)
        endTime = time.time()

        executeTime = endTime - startTime

        # Restore knobs setting
        for i, var in enumerate(self.variables):
            val = prevSetting[i]
            com = command.format(var, val)
            self.mydb.cmd_query(com)
        
        return executeTime
    
    def getReward(self):
        return self.getMetricsVec(self.queries)[0] * 1000

    # TODO: how to generate metrics
    def getMetricsVec(self, queries):
        """
        Generate vector from metrics
        """
        startTime = time.time()
        self.cursor.execute(queries, multi=True)
        endTime = time.time()

        newTime = endTime - startTime
        oldTime = self.getDefaultSettingExecuteTime(queries)
        return [oldTime - newTime]
    
    def currentKnobValue(self):
        value = []
        command = "show session variables like '{}';"
        for knob in self.variables:
            com = command.format(knob)
            val = int(float(self.getValue(com)[0][1]))
            value.append(val)
        return value
    
    def getState(self):
        """
        Concatenate queryVector, metricsVector as state vector
        """
        queries, queryVec = self.defaultWordload, self.queryVec
        # queries, queryVec = self.generateQuery()
        knobVec = self.currentKnobValue()
        metricsVec = self.getMetricsVec(queries)

        totalVec = queryVec + knobVec + metricsVec
        return totalVec
    
    def step(self, a):
        self.executeAction(a)
        s_ = self.getState()
        r = self.getReward()
        return s_, r, False, None
    
    def reset(self):
        """
        Drop all tables
        """
        command = "drop database test1;"
        self.execute(command)
        command = "create database test1;"
        self.execute(command)

        command = "set {}={};"

        # Restore to default setting
        defaultSetting = self.getDefaultSetting()
        for k in defaultSetting.keys():
            val = defaultSetting[k]
            com = command.format(k, val)
            self.execute(command)
        
        return self.getState()
    
    def sysbench_prepare(self):
        command = "sysbench --test=oltp --mysql-table-engine=innodb --oltp-table-size=10000 --mysql-host=47.96.140.67 --mysql-user=root --mysql-password=8888 --mysql-socket=/var/lib/mysql/mysql.sock  prepare"
        os.system(command)

    def sysbench_test(self):
        command = "sysbench --test=oltp --mysql-table-engine=innodb --oltp-table-size=10000 --mysql-host=47.96.140.67 --mysql-user=root --mysql-password=8888 --mysql-socket=/var/lib/mysql/mysql.sock --max-time=3 run > test.txt"
        # os.system(command)

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
        # print(avg_request_time)

    def sysbench_clean(self):
        command="./sysbench --test=oltp --num-threads=5 cleanup"
        os.system(command)

    def setKnobs(self, knobs):
        command = "set session {}={};"
        selectCom = "show session variables like '{}';"

        prevVal = self.currentKnobValue()

        for k in knobs:
            val = knobs[k]
            com = command.format(k, val)
            self.mydb.cmd_query(com)
        
        curVal = self.currentKnobValue()

    def close(self):
        self.cursor.close()
        self.mydb.close()
