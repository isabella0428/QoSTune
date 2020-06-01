import mysql.connector

class Env:
    def __init__(self, variables=None, metrics=None, hostname="47.96.140.67", username="root", password="8888"):
        self.variables = variables          # Knobs to set
        self.metrics = metrics              # Metrics for evaluating performance
        self.mydb = self.login(hostname, username, password)
        self.cursor = self.mydb.cursor()

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
    
    def execute(self, queries):
        """
        Execute workload
        """
        for q in queries:
            self.cursor.execute(q)

    def getQueryVec(self):
        """
        Generate vector from query
        """
        return [1]
    
    def getMetricsVec(self):
        """
        Generate vector from metrics
        """
        vec = []

        for m in self.metrics:
            value = self.getValue(m)
            vec.append(value)
        return vec
    
    def getValue(self, variable):
        """
        Get specfic value from database
        """
        command = "show variables like " + str(variable)
        result = self.cursor.fetchall()

        for res in result:
            return float(res)
    
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
        # Clear all
        return
    
