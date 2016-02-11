#coding:utf-8
import parse
import taskDB 
import common
# data 为处理好的数据 判断其中内容后直接执行相关请求
def routeRequest(raw_data):
	data = parse.parseTo(raw_data,1)	
	if(data[1]=="A"):
		return addTask(raw_data);
	if(data[1]=="L"):
		return listTask(raw_data);
	if(data[1]=="G"):
		return getResult(raw_data);
	if(data[1]=="O"):
		return over(raw_data);

def addTask(data):
	data = parse.parseToAddTask(data)
	taskDB.addTaskInfo(data)
	raw = parse.parseToBin("a",'')
	return raw
def listTask(data):
	task = taskDB.getTaskInfo()
	taskList = []
	for i in task:
		status = i.task_status.encode("utf-8") 
		etc = i.task_etc.encode("utf-8")
		date = long(common.datetimeToTimestamp(i.task_date))
		taskList.append([i.task_ID,status,date,etc])
	return parse.parseToBinList(taskList)
def getResult(data):
	print("gerResult")
def over(data):
	print("over")

