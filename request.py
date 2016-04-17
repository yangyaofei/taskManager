#coding:utf-8
import parse
import taskDB 
import taskManager
import common
from logger import logger
# data 为处理好的数据 判断其中内容后直接执行相关请求


# TODO
#	一个想法,是否应该将server部分作为一个单独的进程而将后
#	台的部分作为另外一个单独的进程,这样做的好处就是server
#	部分由于后台任务管理导致前台不能接受请求和数据的问题
#	但问题是值得这样写么,毕竟不会有这么多的请求.所以先将这
#	个问题列为TODO,等以后没事儿的时候实现


def routeRequest(raw_data):
	data = parse.parseTo(raw_data,1)
	logger.info("identify data["+str(data)+"] and route it")
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
	task_ID = taskDB.addTaskInfo(data)
	logger.debug("add Task to database,task_ID:"+str(task_ID))
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
	task_ID = parse.paresID(raw_data)
	logger.debug("startTask task_ID:"+str(task_ID))
	if taskManager.startTask(task_ID):
		return parse.resposeStartTask()
	else:
		return parse.resposeError()
#TODO
'''def stopTask(raw_data):
def	restartTask(raw_data)
def	editTask(raw_data):
def	getResult(raw_data):
def	deleteResult(raw_data)
'''
