# coding:utf-8
import common
import json

VERSION = 3


class MAIN_KEY:
	version = "version"
	request = "request"
	patamenter = "paramenter"


class TASK_KEY:
	task_ID = "task_ID"
	task_name = "task_name"
	task_create_time = "task_create_time"
	task_finish_time = "task_finish_time"
	task_type = "task_type"
	task_status = "task_status"
	task_para = "task_para"
	task_data = "task_data"


class TASK_STATUS:
	addTask = "a"
	startTasK = "s"
	process = "p"
	complete = "c"
	error = "e"
	pause = "u"


class REQUEST:
	addTask = "A"
	listTask = "L"
	startTask = "B"
	getTask = "C"
	stopTask = "S"
	restartTask = "R"
	editTask = "I"
	deleteTask = "F"
	pauseTask = "P"
	getResult = "G"
	deleteResult = "D"
	ok = "o"
	error = "e"

# 主转换函数
# data 在python中为一个列表


def parseTo(data):
	return json.loads(data)


def parseToJson(request, para_data=""):
	data = {}
	data[MAIN_KEY.version] = VERSION
	data[MAIN_KEY.request] = request
	if 0 != len(para_data):
		data[MAIN_KEY.patamenter] = para_data
	return json.dumps(data, cls=common.JsonEncoder)
# 函数命名规则
# client --> server
# 	client	:	parseToBin+***	 data	>>>	bindata
# 	server	:	parseTo+***		bindata	>>>	data
# server --> client
# 	client	:	parseTo+***		bindata	>>>	data
# 	server	:	respose+***		data	>>> bindata
# 参数:data为整个的rawdata


def parseToBinwithID(task_ID, request):
	data = {TASK_KEY.task_ID: task_ID}
	return parseToJson(request, data)


def parseToBinStartTask(task_ID):
	return parseToBinwithID(task_ID, "B")


def parseToBinStopTask(task_ID):
	return parseToBinwithID(task_ID, "S")


def paresID(data):
	if MAIN_KEY.patamenter not in data:
		return None
	return data[MAIN_KEY.patamenter][TASK_KEY.task_ID]


def resposeStartTask():
	return parseToJson("b", "")


def resposeStopTask():
	return parseToJson("s", "")


def resposeError():
	return parseToJson("e", '')