#coding:utf-8
import parse
import taskDB 
import taskManager
import common
from logger import logger
# data 为处理好的数据 判断其中内容后直接执行相关请求
def routeRequest(raw_data):
	logger.info("identify data and route it")
	data = parse.parseTo(raw_data,1)	
	if(data[1]=="A"):
		return addTask(raw_data);
	elif(data[1]=="L"):
		return listTask(raw_data);
	elif(data[1]=="B"):
		return startTask(raw_data)
	elif(data[1]=="S"):
		return stopTask(raw_data)
	elif(data[1]=="R"):
		return restartTask(raw_data)
	elif(data[1]=="I"):
		return editTask(raw_data)
	elif(data[1]=="G"):
		return getResult(raw_data)
	elif(data[1]=="D"):
		return deleteResult(raw_data)

def addTask(data):
	data = parse.parseToAddTask(data)
	logger.debug("add Task to database")
	task_ID = taskDB.addTaskInfo(data)
	logger.debug("run this Task")
	taskManager.addTask(task_ID,data)
	raw = parse.resposeAddTask()
	return raw
def listTask(data):
	task = taskDB.getAllTaskInfo()
	taskList = []
	for i in task:
		status = i.task_status.encode("utf-8") 
		date = long(common.datetimeToTimestamp(i.task_date))
		data = i.task_data.encode("utf-8")
		error = str(i.task_error).encode("utf-8")
		taskList.append([i.task_ID,status,date,data,error])
	return parse.resposeListTask(taskList)
def	startTask(raw_data):
def stopTask(raw_data):
def	restartTask(raw_data)
def	editTask(raw_data):
def	getResult(raw_data):
def	deleteResult(raw_data)

