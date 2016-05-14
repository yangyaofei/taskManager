# coding:utf-8
import parse
import taskDB
# import taskManager
# import common
from logger import logger
# data 为处理好的数据 判断其中内容后直接执行相关请求


# TODO
# 	一个想法,是否应该将server部分作为一个单独的进程而将后
# 	台的部分作为另外一个单独的进程,这样做的好处就是server
# 	部分由于后台任务管理导致前台不能接受请求和数据的问题
# 	但问题是值得这样写么,毕竟不会有这么多的请求.所以先将这
# 	个问题列为TODO,等以后没事儿的时候实现


def routeRequest(raw_data, queue):
	data = parse.parseTo(raw_data)
	logger.info("identify data[" + str(data) + "] and route it")
	if data[parse.MAIN_KEY[1]] == "A":
		return addTask(data)
	elif data[parse.MAIN_KEY[1]] == "L":
		return listTask(data)
	elif data[parse.MAIN_KEY[1]] == "B":
		return startTask(queue, data)
	elif data[parse.MAIN_KEY[1]] == "S":
		return stopTask(queue, data)
	elif data[parse.MAIN_KEY[1]] == "R":
		return restartTask(data)
	elif data[parse.MAIN_KEY[1]] == "I":
		return editTask(data)
	elif data[parse.MAIN_KEY[1]] == "G":
		return getResult(data)
	elif data[parse.MAIN_KEY[1]] == "D":
		return deleteResult(data)


def addTask(data):
	data = parse.parseToAddTask(data)
	name = data[parse.TASK_ADD[1]]
	type = data[parse.TASK_ADD[0]]
	para = data[parse.TASK_ADD[2]]
	ID = taskDB.addTaskInfo(name, type, para)
	logger.debug("add Task to database,task_ID:" + str(ID))
	raw = parse.resposeAddTask()
	return raw


def listTask(data):
	task = taskDB.getAllTaskInfo()
	taskList = []
	for i in task:
		# create = long(common.datetimeToTimestamp(i.task_create_time))
		# finish = -1
		# if type(None) != type(i.task_finish_time):
		# 	finish = long(common.datetimeToTimestamp(i.task_finish_time))
		item = {
			parse.TASK_KEY[0]: i.task_ID,
			parse.TASK_KEY[1]: i.task_name,
			parse.TASK_KEY[2]: i.task_create_time,
			parse.TASK_KEY[3]: i.task_finish_time,
			parse.TASK_KEY[4]: i.task_type,
			parse.TASK_KEY[5]: i.task_status,
			parse.TASK_KEY[6]: i.task_para,
			parse.TASK_KEY[7]: i.task_data
		}
		taskList.append(item)
	return parse.resposeListTask(taskList)


def startTask(queue, data):
	queue.put(data)
	task_ID = parse.paresID(data)
	logger.info("startTask task_ID:" + str(task_ID))
	return parse.resposeStartTask()


def stopTask(queue, data):
	queue.put(data)
	task_ID = parse.paresID(data)
	queue.put(data)
	return parse.resposeStopTask()


# TODO
'''def	restartTask(raw_data)
def	editTask(raw_data):
def	getResult(raw_data):
def	deleteResult(raw_data)
'''
