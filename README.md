# QoSTune
QoSTune project -- Using RL to find a better database configuration



## Execution Plan

#### 1. Installization

- [ ] Install Mysql on remote server

  Include configure to allow remote access and grant root priviledge

- [ ] Install mysql connecter (eg: python)

  https://www.runoob.com/python3/python-mysql-connector.html

  Get familiar with sql commands with python, know how to modify data with python

- [ ] Know how to configure database with sql command ==> also can modify parameter using python

  https://blog.csdn.net/u014665013/article/details/78608286 => Method 2



#### 2. Get data

- [ ] Generate Workload

  Not sure how to do it, maybe we can find some code in github

- [ ] Get system status data of database

  Like throughput, latency (Using mysql connector in python)

- [ ] Get user latency data

  Not sure how to do it, maybe we can just use timer to calculate (Do it by ourselves)



#### 3. Train model

- [ ] Use data from Step2 and train RL model