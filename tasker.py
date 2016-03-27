#coding:utf-8
#此模块用于task执行
'''
				fork() execl() kill
	taskManager----------------------->tasker
	

taskManager:
	由request调用,然后在taskManager中进行数据库的存储,fork等工作
	维护一个临时列表,记录子进程(tasker)的状态以及PID,并与数据库中比较,
如果不同,则进行更新,特别是已经不存在的进程则标记为error或者stop
	维护临时列表的时间是在request调用时调用
tasker:
	由taskManger fork后利用execl执行tasker,仅执行任务,并把任务状态实时
写入数据库中,不与taskeManager通信.
		
'''
import urllib
import urllib2
import hashlib
import json
import time
import rawdataDB
import multiprocessing
import taskDB
url = "http://server2.zhchtd.com:22280/getprojectjson"
KEY = "zhuanlikey"
ID = -1
def getData(url,values):
	data = urllib.urlencode(values)
	req  = urllib2.Request(url,data)
	return json.loads(urllib2.urlopen(req).read())
def generateCode(time):
	key = hashlib.md5((str(time)+KEY).encode("utf-8")).hexdigest()
	key = hashlib.md5(key.encode("utf-8")).hexdigest()
	return key
def generateValues(sql):
	ts = long(time.time())
	key = generateCode(ts)
	values = {
				"code":key,
				"time":str(ts),
				"where":sql
			}
	return values
def getIDs(reqdata):
	if int(reqdata["status"])== 0:
		return reqdata["list"]
	else:
		print(reqdata["message"])
		return []
def taskerStatus(ID,status,message):
	data = taskDB.getTaskInfo(ID)
	data.task_status = status
	data.task_etc = message
	taskDB.changeTask(data)
def taskerToError(ID,message):
	# 转到出错状态 并保存出错原因
	taskerStatus(ID,'e',message)
def tsakerToComplete(ID):
	taskerStatus(ID,'c','')
# start tasker
def startTasker(task_ID,SQL):
	zl_IDs = getData(url,generateValues(SQL))
	error = zl_IDs["message"]
	zl_IDs = getIDs(zl_IDs) 
	#test 
	i =		3990000
	while i<4000000:
		zl_IDs.append(i)
		i+=1
	# test end '''
	if(len(zl_IDs) == 0 ):
	#	taskerToError(task_ID,"获取数据ID失败! :" + str(error))
		print(str(error))
		exit(-1)
	# Use a prosess to get data from DataBase
	MAX_QUEUE = 100
	queue = multiprocessing.Queue(MAX_QUEUE)
	p = Producer(queue,zl_IDs,1000)
	p.start()
	data = []
	# Get data use queue and Process it
	while True: 
		print("in while")
		dirt = queue.get()
		if dirt["flag"] == "e":
			print("get an e flag")
			break
		for d in dirt["data"]:
			print(d.id),
			#print(d.apply_num),
			print(" "),
		print("")
	p.join()
	
	#'''
# 生产者 用来从database获取数据,并传输给主进程进行处理
# 传输数据是一个字典,flag和data,flag为d的时候证明传输的
# 是数据,当flag的值为e的时候表示数据已经传输完毕
class Producer(multiprocessing.Process):
	def __init__(self,queue,zl_IDs,step):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.zl_IDs = zl_IDs
		self.step = step
	def run(self):
		iterator = 0
		IDs = self.zl_IDs
		queue = self.queue
		step = self.step
		while iterator < len(IDs):
			data = []
			dirt = {}
			if iterator > (len(IDs)-step):
				print(iterator)
				data = rawdataDB.getFromIDs(IDs[iterator:])
			else:
				print(str(iterator)+"-"+str(iterator+step))
				data = rawdataDB.getFromIDs(IDs[iterator:iterator+step])
			dirt["flag"] = "d"
			dirt["data"] = data
			queue.put(dirt)
			iterator+=step
		dirte = {}
		print("put an e flag")
		dirte["flag"] = "e"
		queue.put(dirte)
		queue.close()
