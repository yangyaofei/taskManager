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
# step为每次获取的ID数
def getDataProcess(IDs,step,queue):
	iterator = 0
	data = []
	while iterator < len(IDs):
		if iterator > (len(IDs)-step):
			data = rawdataDB.getFromIDs(IDs[iterator:])
			queue.put(data)
		else:
			data = rawdataDB.getFromIDs(IDs[iterator:iterator+step])
			queue.put(data)
		iterator+=step
	queue.close()
# start tasker
def startTasker(task_ID,SQL):
	zl_IDs = getData(url,generateValues(SQL))
	error = zl_IDs["message"]
	zl_IDs = getIDs(zl_IDs) 
	
	if(len(zl_IDs) == 0 ):
	#	taskerToError(task_ID,"获取数据ID失败! :" + str(error))
		print(str(error))
		exit(-1)
	#Use a prosess to get data from DataBase
	MAX_QUEUE = 100
	queue = multiprocessing.Queue(MAX_QUEUE)
	process = multiprocessing.process(target=getDataProcess,args=(IDs,100,queue))
	process.start()
	process.join()
	data = []
	while not queue.empty():
		data = queue.get()
		for d in data:
			print(d.id),
			print(" "),
		print("")
	


